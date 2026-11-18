import calendar
import random
from datetime import date, time
from html import escape
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task
from rag import reply

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.markdown(f"<style>{(Path(__file__).parent / 'style.css').read_text()}</style>", unsafe_allow_html=True)



def sky_html():
    """Ghibli-style background: twinkling stars, floating light motes and soft clouds (CSS only)."""
    r = random.Random(11)  # same positions every run
    stars = "".join(
        f"<i style='left:{r.randint(2, 97)}%;top:{r.randint(3, 90)}%;width:{(w := r.randint(14, 28))}px;height:{w}px;"
        f"animation-duration:{r.uniform(3, 6):.1f}s;animation-delay:-{r.uniform(0, 6):.1f}s'></i>" for _ in range(34))
    motes = "".join(
        f"<u style='left:{r.randint(0, 98)}%;width:{(w := r.randint(8, 18))}px;height:{w}px;"
        f"animation-duration:{r.uniform(16, 30):.0f}s;animation-delay:-{r.uniform(0, 30):.0f}s'></u>" for _ in range(16))
    clouds = "".join(
        f"<b style='top:{top}%;width:{w}px;animation-duration:{d}s;animation-delay:-{delay}s'></b>"
        for top, w, d, delay in [(6, 140, 130, 20), (24, 100, 160, 90), (62, 120, 190, 40)])
    return f"<div class='sky'>{clouds}{stars}{motes}</div>"


st.markdown(sky_html(), unsafe_allow_html=True)

EMOJI = {"dog": "🐶", "cat": "🐱", "other": "🐰"}
IMPORTANCE = {"🌱 not very": 1, "🌼 normal": 2, "🌸 very": 3}
HOW_OFTEN = {"just once": "once", "every day": "daily", "every week": "weekly"}

# ------------------------------------------------------------------ state
# (the owner lives in session_state so it survives reruns)
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
    st.session_state.chat_open = False
    st.session_state.animate = False
    st.session_state.messages = [{"role": "assistant", "content":
        "Woof! 🐶 I know what's on your calendar. Ask me **“what is Buddy doing today?”** or say "
        "**“add a walk for Buddy at 5pm tomorrow”**."}]
owner = st.session_state.owner
scheduler = Scheduler(owner)


def shift_month(step):
    """Button callback: move the selected day one month back/forward."""
    d = st.session_state.day
    month = d.month - 1 + step
    year, month = d.year + month // 12, month % 12 + 1
    st.session_state.day = date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


def toggle_chat():
    st.session_state.chat_open = not st.session_state.chat_open


def tasks_on(pet, day):
    return sorted((t for t in pet.tasks if t.due_date == day), key=lambda t: t.due_time or time.max)


def clock(t):
    return t.due_time.strftime("%I:%M %p").lstrip("0") if t.due_time else "any time"


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.title("🐾 PawPal+")
    owner.name = st.text_input("What's your name?", owner.name)
    day = st.date_input("Jump to a date", value=date.today(), key="day")

    st.subheader("🐶 Add a pet")
    with st.form("pet_form", clear_on_submit=True):
        pet_name = st.text_input("What's your pet's name?", placeholder="e.g. Buddy")
        species = st.selectbox("What kind of pet?", ["dog", "cat", "other"])
        if st.form_submit_button("Add my pet") and pet_name.strip():
            owner.add_pet(Pet(pet_name.strip(), species))
            st.rerun()
    st.caption("Every pet gets its own tab →")

# ------------------------------------------------------------------ main
st.title(f"{owner.name}'s day · {day:%B %d}")
tab_names = ["📅 Calendar", "🖨 Schedule"] + [f"{EMOJI.get(p.species, '🐰')} {p.name}" for p in owner.pets]
tabs = st.tabs(tab_names)

# ---------- calendar (month grid) ----------
with tabs[0]:
    c1, c2, c3 = st.columns([1, 4, 1])
    c1.button("◀ earlier", on_click=shift_month, args=(-1,))
    c2.subheader(f"{calendar.month_name[day.month]} {day.year}")
    c3.button("later ▶", on_click=shift_month, args=(1,))

    cells = "".join(f"<div class='dow'>{d}</div>" for d in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
    for week in calendar.Calendar(firstweekday=6).monthdatescalendar(day.year, day.month):
        for d in week:
            events = sorted(((p, t) for p in owner.pets for t in p.tasks if t.due_date == d),
                            key=lambda pt: pt[1].due_time or time.max)
            pills = "".join(
                f"<div class='pill {'req' if t.required else ''}'>{EMOJI.get(p.species, '🐰')} {clock(t).replace(' ', '')} "
                f"{escape(t.description)}</div>" for p, t in events[:3])
            more = f"<div class='more'>+{len(events) - 3} more</div>" if len(events) > 3 else ""
            classes = "cell" + (" other" if d.month != day.month else "") + (" sel" if d == day else "") \
                + (" today" if d == date.today() else "")
            cells += f"<div class='{classes}'><span class='num'>{d.day}</span>{pills}{more}</div>"
    st.markdown(f"<div class='cal'>{cells}</div>", unsafe_allow_html=True)
    if not owner.pets:
        st.info("Add your first pet in the sidebar to get started 🐾")
    else:
        st.caption("Pink = required task. Pick a date in the sidebar, then open a pet's tab to add tasks.")

# ---------- typewriter schedule ----------
with tabs[1]:
    if st.button("🖨 Print my schedule"):
        st.session_state.animate = True
    pet_of = {id(t): p for p in owner.pets for t in p.tasks}
    todays = scheduler.sort_by_time([t for t in owner.get_all_tasks() if t.due_date == day])

    lines = [f"<div class='line title'>✿ {escape(owner.name)}'s day · {day:%b %d} ✿</div>"]
    for t in todays:
        mark = "✓" if t.completed else "★" if t.required else "·"
        lines.append(f"<div class='line'>{mark} {clock(t):>8}  {escape(t.description)} "
                     f"({escape(pet_of[id(t)].name)}) {t.duration}m</div>")
    if not todays:
        lines.append("<div class='line'>nothing planned yet ♡</div>")
    # each line starts typing a little after the one before it
    lines = [l.replace("class='line", f"style='animation-delay:{i * 1.2}s' class='line", 1) for i, l in enumerate(lines)]
    animate = "animate" if st.session_state.animate else ""
    st.session_state.animate = False
    st.markdown(f"<div class='paper {animate}'>{''.join(lines)}</div>"
                "<div class='machine'>♡ PawPal Typewriter ♡<div class='keys'>● ● ● ● ● ● ● ●</div></div>",
                unsafe_allow_html=True)
    for msg in scheduler.find_conflicts():
        st.warning(msg.removeprefix("Warning: "))
    st.caption("★ = required · ✓ = done")

# ---------- one tab per pet ----------
for tab, pet in zip(tabs[2:], owner.pets):
    with tab:
        st.subheader(f"{EMOJI.get(pet.species, '🐰')} {pet.name}'s tasks · {day:%b %d}")
        mine = tasks_on(pet, day)
        if not mine:
            st.info(f"{pet.name} has nothing planned for this day. Add a task below, or ask the dog in the corner 🐶")
        for t in mine:
            col1, col2 = st.columns([8, 1])
            label = f"{clock(t)} · {t.description} ({t.duration} min){' ★' if t.required else ''}"
            if col1.checkbox(label, value=t.completed, key=f"chk_{id(t)}", disabled=t.completed):
                if not t.completed:
                    scheduler.mark_task_complete(pet, t)
                    st.rerun()
            if col2.button("🗑", key=f"del_{id(t)}", help="Remove this task"):
                pet.remove_task(t)
                st.rerun()

        st.markdown(f"##### ➕ Add a task for {pet.name}")
        with st.form(f"task_form_{pet.name}", clear_on_submit=True):
            title = st.text_input("What needs doing?", placeholder="e.g. Evening walk")
            c1, c2 = st.columns(2)
            minutes = c1.number_input("How long? (minutes)", 1, 240, 20)
            when = c2.time_input("What time?", time(8, 0))
            c3, c4 = st.columns(2)
            importance = c3.selectbox("How important is it?", list(IMPORTANCE), index=1)
            often = c4.selectbox("How often?", list(HOW_OFTEN))
            if st.form_submit_button("Add to calendar") and title.strip():
                pet.add_task(Task(title.strip(), when, int(minutes), IMPORTANCE[importance],
                                  HOW_OFTEN[often], day, required=IMPORTANCE[importance] == 3))
                st.rerun()

# ------------------------------------------------------------------ the dog in the corner + chat
is_open = st.session_state.chat_open
st.button("🐕" if is_open else "🐶", key="dog_awake" if is_open else "dog_sleep", on_click=toggle_chat,
          help="Tap me to close the chat" if is_open else "Shh, I'm sleeping… tap to wake me up!")

if is_open:
    st.markdown("<div class='walker'><span>🐕</span></div>", unsafe_allow_html=True)
    with st.container(key="chatpanel"):
        st.subheader("💬 Ask PawPal")
        with st.container(height=300):
            for m in st.session_state.messages:
                st.chat_message(m["role"], avatar="🐾" if m["role"] == "assistant" else "💜").write(m["content"])
        if prompt := st.chat_input("Ask me anything… 🐾"):
            text, added = reply(prompt, owner, day)
            st.session_state.messages += [{"role": "user", "content": prompt}, {"role": "assistant", "content": text}]
            if added:
                st.session_state.animate = True
            st.rerun()
