# Model Card: PawPal+ Chat

## 1. What it is
A small **RAG chatbot** for pet care. For each message it **retrieves** from two places:
1. the care guidelines in `knowledge/care_guidelines.json` (14 entries: tips, usual durations and times, by species), and
2. the owner's own tasks on the calendar,

then **builds its reply or new tasks from what it found**. It is keyword retrieval plus templates, so it is predictable,  and testable. Built on top of my **PawPal+ ** project (`Owner`, `Pet`, `Task`, `Scheduler`).

**Intended use:** an individual pet owner organizing everyday care. **Not** a veterinary tool.

## 2. Testing results
Reproduce with `pytest -v` (full output is in the README) and `python demo.py`.

| Test input | What I checked | Result |
|---|---|---|
| "what should I feed my cat?" | Only the cat answers, using the retrieved tip | Pass |
| "build a routine for my dog and cat" | 8 tasks added, 0 same-time conflicts | Pass |
| "add a walk for Buddy at 5pm" | Task created at 17:00 | Pass |
| "add a walk for Buddy at 5pm on nov 20" | Task lands on Nov 20 | Pass |
| "what is Buddy doing today?" | Lists only Buddy's real tasks for that day | Pass |
| "what is Mochi doing?" (nothing planned) | Says there is nothing planned | Pass |
| "add a dog named buddy … walk on nov 20th at 8am" | Pet created, walk on Nov 20 at 8:00 | Pass |
| "I got a new kitten called Luna" | Pet added as a cat, no task invented | Pass |
| "add a dog named Buddy" twice | No duplicate pet | Pass |
| "add a bunny named Clover and build a routine" | Saved as species "other", gets tasks | Pass |
| Same routine requested twice | No duplicate tasks | Pass |
| Empty message / no pets / "quantum physics" | Friendly reply, no crash | Pass |
| Original PawPal tests (sorting, recurring tasks, conflicts) | Still work | Pass |

**25 of 25 pytest tests pass.** 

## 3. Limitations and biases
- **Small knowledge.** Only 14 topics, and only dogs, cats and a catch-all "other". Anything else gets "I don't know".
- **Generic guidelines, written by me.** Durations and times (e.g. a 30-minute dog walk, meals at 7:30 AM and 6 PM) describe a typical adult dog or cat. They don't fit puppies, seniors, special diets, medical conditions, or very active breeds.
- **Assumes a certain owner.** The default day assumes someone is home in the morning and evening, uses US-style 12-hour times and English phrasing.
- **Keyword matching is fragile.** It can't handle typos, slang or other languages. A word like "feed" matches both breakfast and dinner, so it shows both tips.
- **Time parsing needs am/pm.** "8am" works; a bare "at 8" is not understood, and it falls back to the guideline's usual time.
- **One new pet per message.** "add a dog named Buddy and a cat named Mochi" only adds Buddy.
- **No saving.** Data lives in the browser session only. Refresh the page and it's gone.
- **Weak conflict check.** Tasks are only kept apart if they start at the same minute. Two tasks whose durations overlap (a 30-minute walk at 8:00 and a task at 8:10) are not caught.

## 4. Misuse and prevention
| Risk | What I did about it |
|---|---|
| **Mistaken for vet advice** (tips, medication timing) | Tips are general, never include doses, and this card states it is not a vet tool. *Still missing:* an on-screen disclaimer. |
| **Over-trusting a wrong or odd answer** | The reply shows exactly what was added. Every task can be ticked off or deleted (🗑) in the pet's tab. When it doesn't know, it says so instead of guessing. |
| **Script/HTML injection through pet or task names** | Anything a user types is HTML-escaped before it is drawn on the calendar or typewriter paper. |
| **Someone using it to plan unsafe care** (e.g. skipping meals) | It only schedules tasks the owner asks for plus standard routines. It doesn't recommend skipping care. A fuller version should warn about unsafe requests. |

## 5. What surprised me while testing reliability
- **A date I thought worked didn't.** "nov 20th" failed to parse because my pattern expected the number to end the word. The "th" broke it. I only found this when I tested the exact sentence I wanted the chat to handle.
- **"Today" means two things.** My test failed because the calendar's *selected* day and the real *today* are different. The chat is right to use the real today when you say "today". The test was wrong, which taught me to check whether the code or the test is at fault.
- **A bad font setting made everything look wrong.** The look felt "off" until I traced it to one leftover `font = "monospace"` line in the Streamlit config.
- **The boring tests mattered most.** Empty input, no pets and unknown topics each needed their own handling, and none of them show up in a happy-path demo.

## 6. Collaboration with AI
I built this with some Claude Code mostly for the look of the app, I did most of it by myself but it also did help with testcases and making a plan of what to keep and what to improve. It inspected my existing files first, then I wrote code, ran the tests and took screenshots, while I also set the goals and, the look (lavender and pink, the typewriter,the Ghibli sky) and decided what was too much.

**One suggestion I accepted: reuse my existing `Scheduler` and data classes.** Instead of writing new scheduling code,  the chat suggested building on top of `Owner`, `Pet`, `Task` and `Scheduler`. I accepted it because those classes were already tested, so the I only needed to *create tasks*. The calendar, conflict warnings and tick-offs all work without new logic.

**One suggestion I did not accept as written: the big "agent" version.** The AI's first version suggested a large planner with a plan → verify → repair loop, a logger, optional language-model parsing, and a custom pixel-art theme, spread over many files. It  was far too long and complicated. I asked for a much simpler version, something that would push me but also something I could get done.


