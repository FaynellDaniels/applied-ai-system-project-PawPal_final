"""A tiny RAG helper for PawPal+.

It retrieves from TWO places before it answers:
  1. the care guidelines  (knowledge/care_guidelines.json)  -> tips, durations, times
  2. the owner's own tasks (what is already on the calendar) -> "what is Buddy doing today?"
"""

import json
import re
from datetime import date, time, timedelta
from pathlib import Path

from pawpal_system import Pet, Task

KB = json.loads((Path(__file__).parent / "knowledge" / "care_guidelines.json").read_text())

STATUS_WORDS = {"tasks", "task", "doing", "agenda", "calendar", "next", "left", "done", "upcoming", "busy"}
ADD_WORDS = {"add", "remind", "book", "put"}
ROUTINE_WORDS = {"routine", "plan", "schedule", "day"}
HELLO_WORDS = {"hi", "hello", "hey", "help"}
SPECIES_OF = {"dog": "dog", "puppy": "dog", "cat": "cat", "kitten": "cat", "rabbit": "other", "bunny": "other",
              "hamster": "other", "bird": "other", "fish": "other", "turtle": "other"}
NEW_PET_RE = re.compile(r"\b(" + "|".join(SPECIES_OF) + r")\b.{0,25}?\b(?:named|called)\s+([A-Za-z]+)", re.I)
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def words(text):
    found = set(re.findall(r"[a-z]+", text.lower()))
    return found | {w.rstrip("s") for w in found}  # "dogs" also matches "dog"


def species_ok(guideline, species):
    return species in guideline["species"] or "any" in guideline["species"]


def retrieve(question, species, top=2):
    """Return the guidelines whose keywords best match the question (best first)."""
    q = words(question)
    scored = []
    for g in KB:
        if species_ok(g, species):
            hits = len(q & words(" ".join(g["keywords"])))
            if hits:
                scored.append((hits, g))
    scored.sort(key=lambda pair: -pair[0])
    return [g for _, g in scored[:top]]


def to_time(hhmm):
    hour, minute = hhmm.split(":")
    return time(int(hour), int(minute))


def find_time(text):
    """Pull a time like '5pm' or '7:30 am' out of text (None if there isn't one)."""
    m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)", text.lower())
    if not m:
        return None
    hour = int(m.group(1)) % 12 + (12 if m.group(3) == "pm" else 0)
    return time(hour, int(m.group(2) or 0))


def find_day(text, selected_day, today=None):
    """Understand 'today', 'tomorrow', 'friday', 'nov 20'. Falls back to the calendar's selected day."""
    today = today or date.today()
    low = text.lower()
    if "tomorrow" in low:
        return today + timedelta(days=1)
    if "today" in low:
        return today
    for i, name in enumerate(WEEKDAYS):
        if name in low:
            return today + timedelta(days=(i - today.weekday() - 1) % 7 + 1)
    m = re.search(r"\b(" + "|".join(MONTHS) + r")[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b", low)
    if m:
        try:
            result = date(today.year, MONTHS.index(m.group(1)) + 1, int(m.group(2)))
            return result if result >= today else result.replace(year=today.year + 1)
        except ValueError:
            pass
    return selected_day


def make_task(guideline, day, when=None, taken=()):
    """Turn a guideline into a Task. If the time is taken, nudge it 5 minutes (no conflicts)."""
    when = when or to_time(guideline["preferred_time"])
    minutes = when.hour * 60 + when.minute
    while (when.hour, when.minute) in taken:
        minutes += 5
        when = time(minutes // 60 % 24, minutes % 60)
    return Task(guideline["title"], due_time=when, duration=guideline["default_duration"],
                priority=guideline["priority"], due_date=day, required=guideline["required"])


def busy_times(owner, day):
    return {(t.due_time.hour, t.due_time.minute) for t in owner.get_all_tasks()
            if t.due_date == day and t.due_time}


def agenda(pets, day, q):
    """RETRIEVE the owner's own tasks for a day and describe them."""
    only_pending = bool(q & {"next", "left"})
    lines = []
    for pet in pets:
        tasks = sorted((t for t in pet.tasks if t.due_date == day and not (only_pending and t.completed)),
                       key=lambda t: t.due_time or time.max)
        if "next" in q:
            tasks = tasks[:1]
        if not tasks:
            lines.append(f"**{pet.name}** has nothing {'left ' if only_pending else ''}on {day:%b %d}. 🌸")
            continue
        items = [f"- {t.due_time:%I:%M %p} · {t.description} ({t.duration} min){' ✓' if t.completed else ''}"
                 if t.due_time else f"- {t.description}" for t in tasks]
        lines.append(f"**{pet.name}** on {day:%b %d}:\n" + "\n".join(items))
    return "\n\n".join(lines)


def reply(message, owner, day):
    """Answer a chat message. `day` is the day selected on the calendar.
    Returns (text, list_of_new_tasks_already_added)."""
    message = message.strip()
    if not message:
        return "Ask me something, like “what is Buddy doing today?” 🐾", []

    # "add a dog named Buddy ..." -> create the pet first, then handle the rest of the message
    new_pet, prefix = None, ""
    found = NEW_PET_RE.search(message)
    if found and words(message) & {"add", "new", "adopt", "got", "get", "have"}:
        name = found.group(2).capitalize()
        new_pet = next((p for p in owner.pets if p.name.lower() == name.lower()), None)
        if new_pet is None:
            new_pet = Pet(name, SPECIES_OF[found.group(1).lower()])
            owner.add_pet(new_pet)
            prefix = f"Added **{name}** ({new_pet.species}) to your pets. They have their own tab now 🐾\n\n"
        else:
            prefix = f"**{name}** is already one of your pets. "

    if not owner.pets:
        return "Add a pet in the sidebar first, then I can help! 🐶", []

    q = words(message)
    if q & HELLO_WORDS and len(q) < 8 and not new_pet:
        return ("Woof, hi! 🐶 I know what's on your calendar and I know pet care. Try:\n\n"
                "- *add a dog named Rex and put him on the schedule for a walk on nov 20th at 8am*\n"
                "- *what is Buddy doing today?*\n- *build a routine for my cat tomorrow*\n"
                "- *add a walk for Buddy at 5pm on Friday*\n- *what should I feed my dog?*"), []

    # which pets? named ones, else dog/cat words, else everyone
    pets = [p for p in owner.pets if p.name.lower() in q]
    pets = pets or [p for p in owner.pets if p.species in q]
    pets = pets or owner.pets
    if new_pet:
        pets = [new_pet]
    target_day = find_day(message, day)

    # 1) questions about what is already planned
    if q & STATUS_WORDS and not new_pet:
        return agenda(pets, target_day, q), []

    added = []
    taken = busy_times(owner, target_day)

    def add_task(pet, g, when=None):
        task = make_task(g, target_day, when, taken)
        taken.add((task.due_time.hour, task.due_time.minute))
        pet.add_task(task)
        added.append(task)
        return f"Added **{g['title']}** for {pet.name} on {target_day:%b %d} at {task.due_time:%I:%M %p} ({task.duration} min) 📅"

    # 2) add one task to the calendar
    if q & ADD_WORDS or new_pet:
        lines = [add_task(pet, g, find_time(message)) for pet in pets for g in retrieve(message, pet.species, top=1)]
        if lines:
            return prefix + "\n\n".join(lines), added
        if new_pet and not q & ROUTINE_WORDS:  # just a new pet, no task mentioned
            return prefix + "Want a routine for them? Say “build a routine for " + new_pet.name + "”.", []

    # 3) a whole routine
    if q & ROUTINE_WORDS:
        for pet in pets:
            have = {t.description for t in pet.tasks if t.due_date == target_day}
            for g in KB:
                if g["routine"] and species_ok(g, pet.species) and g["title"] not in have:
                    add_task(pet, g)
        names = " & ".join(p.name for p in pets)
        if not added:
            return prefix + f"{names} already have a full routine for {target_day:%b %d} ✨", []
        return prefix + (f"Done! I looked up care guidelines for {names} and added {len(added)} tasks "
                f"to {target_day:%b %d}. Open the **🖨 Schedule** tab to watch the typewriter ✨"), added

    # 4) care tips
    lines = [f"**{pet.name} · {g['title']}:** {g['tip']} (about {g['default_duration']} min, "
             f"around {to_time(g['preferred_time']):%I:%M %p})"
             for pet in pets for g in retrieve(message, pet.species)]
    if not lines:
        return ("Hmm, I don't know about that yet. Try asking what a pet is doing today, or about feeding, "
                "walks, play, medication, grooming, litter or vet visits 💜"), []
    return prefix + "\n\n".join(lines), added
