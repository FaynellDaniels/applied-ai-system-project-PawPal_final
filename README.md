# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

<<<<<<< HEAD
- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan
=======
## 🌱 Base project
**PawPal+ ** was a Streamlit app built with Python classes (`Owner → Pet → Task` plus a `Scheduler`). It let you add pets and tasks, sort them by time, spot same-time conflicts, repeat daily/weekly tasks, and build a plan that fits your free time. All of that is still here and still tested.
>>>>>>> 49924e6 (:README final edits)

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
<<<<<<< HEAD
=======

# 4. run the app, it opens in your browser
streamlit run app.py
```
 Then: pick a date → add a pet in the sidebar (or just tap the sleeping dog and chat) → open the **🖨 Schedule** tab and press **Print**.

Optional: `pytest` runs the tests, and `python demo.py` prints the sample chat below.

## 💬 Sample interactions
Real, unedited output of `python demo.py` (re-run it to reproduce):

```text
You:    add a dog named Buddy and put him on the schedule for a walk on nov 20th at 8am
PawPal: Added **Buddy** (dog) to your pets. They have their own tab now 🐾

Added **Morning walk** for Buddy on Nov 20 at 08:00 AM (30 min) 📅

You:    add a cat named Mochi
PawPal: Added **Mochi** (cat) to your pets. They have their own tab now 🐾

Want a routine for them? Say “build a routine for Mochi”.

You:    build a routine for Mochi on nov 18
PawPal: Done! I looked up care guidelines for Mochi and added 4 tasks to Nov 18. Open the **🖨 Schedule** tab to watch the typewriter ✨

You:    what is Buddy doing on nov 20?
PawPal: **Buddy** on Nov 20:
- 08:00 AM · Morning walk (30 min)

You:    what should I feed my cat?
PawPal: **Mochi · Breakfast:** Cats usually prefer 2-3 small meals; always leave fresh water out. (about 5 min, around 07:30 AM)

**Mochi · Dinner:** Wet food should not sit out longer than about 30 minutes. (about 5 min, around 06:00 PM)

You:    quantum physics
PawPal: Hmm, I don't know about that yet. Try asking what a pet is doing today, or about feeding, walks, play, medication, grooming, litter or vet visits 💜
>>>>>>> 49924e6 (:README final edits)
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Implementation Summary
The implementation builds the PawPal system using several classes that work together to manage pet owners, pets, preferences, and scheduling. The Owner class stores information about pet owners and their preferences, while the Pet class represents individual pets and their details. The Schedule class manages scheduled activities or appointments for pets, and the Scheduler class helps create and organize these schedules. Together, these classes allow the system to connect owners with their pets, use owner preferences, and manage pet-related schedules in an organized way.

## 🖥️ Sample Output

<<<<<<< HEAD
Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
==============================================
  Today's Schedule - Jordan
==============================================
  TIME      TASK              PET        LENGTH
----------------------------------------------
   7:30 AM  Morning walk      Buddy       30 min
   8:00 AM  Breakfast         Whiskers    10 min
  12:00 PM  Give medication   Buddy        5 min
   6:30 PM  Play session      Whiskers    20 min
----------------------------------------------
  4 tasks, 65 min total

```

## 🧪 Testing PawPal+
=======
```text
================================== test session starts   ===================================
platform darwin -- Python 3.13.15, pytest-9.2.0, pluggy-1.7.0
rootdir: /Users/nellie/Desktop/cd applied-ai-system-final/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.16.0
collected 25 items                                                                       

tests/test_pawpal.py ..........                                                    [ 40%]
tests/test_rag.py ...............                                                  [100%]

=================================== 25 passed in 0.03s ===================================
```

**What worked:** tests caught real bugs early. The date "nov 20th" didn't parse at first, and a test about "today" showed the chat uses the real today, not the calendar's selected date.
**What didn't / limits:** the chat only knows 14 topics, and the tests cover the logic, not how the page looks. 
**What I learned:** testing the boring cases (empty input, no pets, unknown topic) matters as much as testing the happy path.
>>>>>>> 49924e6 (:README final edits)

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
=============================================================== test session starts ================================================================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/nellie/Documents/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 10 items                                                                                                                                 

tests/test_pawpal.py ..........                                                                                                              [100%]

================================================================ 10 passed in 0.03s ================================================================
```


- The 10 tests cover four areas:

- Basic behavior: mark_complete() changes a task's status, and adding a task to a pet increases its task count.

- Sorting: sort_by_time() returns tasks from all pets in chronological order. It puts tasks with no time last, and returns an empty list when there are no tasks.

- Recurring tasks: completing a daily task creates a new one due tomorrow. A weekly task creates one due in 7 days, and a one-time task creates nothing.

- Conflict detection: two tasks at the same time produce a warning naming both. Tasks at different times produce none.


- Confidence Level - 4.5

## 📐 Smarter Scheduling



| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_by_time(), Scheduler.prioritize_tasks() | Sorts by time of day (earliest first, tasks with no time last), or by priority (highest first, then earliest time) |
| Filtering | Scheduler.filter_tasks() | Filters by completion status (completed=True/False), by pet (pet_name="Buddy"), or both |
| Conflict handling | Scheduler.find_conflicts() | Returns a warning when two pending tasks share the same date and start time (same pet or different pets); overlapping durations are not checked |
| Recurring tasks | Scheduler.mark_task_complete(), Task.next_occurrence() | Completing a "daily" task adds a copy due tomorrow; a "weekly" task adds one due in 7 days |


## 📸 Demo Walkthrough

## Main UI Features and User Actions

The PawPal+ interface allows the user to enter an owner's name, add a pet, select the pet's species, and add pet-care tasks. The user can enter a task name, duration, and priority, then click Add task to add it to the task list. The current tasks are displayed in a table. The user can also select Generate schedule to create a schedule.

## Example Workflow

1. User enters the owner's name, such as "Jordan."

2. User enters a pet's name, such as "Buddy," and selects "Dog" as the species.

3. User enters a task such as "Morning walk," along with its duration and priority.

4. User clicks Add task, and the task appears in the task list.

5. User adds additional tasks for Buddy or another pet, such as feeding, medication, or grooming.

6. The system stores the pets under the Owner and the tasks under each Pet.

7. The Scheduler collects the tasks from the owner and can sort them by time.

8. The scheduler can identify conflicts when two tasks are scheduled for the same time.

9. The user can view pending tasks or tasks belonging to a specific pet.

10. When a recurring task is completed, the scheduler creates its next occurrence. For example, completing a daily breakfast task creates another breakfast task for the following day.

## Key Scheduler Behaviors

- The Scheduler can sort tasks in chronological order, filter tasks by completion status or pet, detect conflicts between tasks scheduled at the same time, and prioritize pending tasks. It can also generate a care plan based on the amount of available time. Daily and weekly tasks automatically receive a new occurrence when completed, while one-time tasks do not repeat.

## Sample CLI Output
```
==============================================
  Today's Schedule - Jordan
==============================================
  TIME      TASK              PET        LENGTH
----------------------------------------------
  7:30 AM   Morning walk      Buddy       30 min
  8:00 AM   Breakfast         Whiskers    10 min
  12:00 PM  Give medication  Buddy        5 min
  6:30 PM   Play session      Whiskers    20 min
----------------------------------------------
  4 tasks, 65 min total

Tasks as added (out of order):
  18:30  Play session
  12:00  Give medication
  08:00  Breakfast
  07:30  Morning walk

Sorted by time:
  07:30  Morning walk
  08:00  Breakfast
  12:00  Give medication
  18:30  Play session

Pending tasks only:
  Play session
  Breakfast
  Morning walk

Buddy's tasks only:
  Give medication
  Morning walk

Checking for conflicts:
  Warning: 08:00 AM conflict - Breakfast (Whiskers) and Grooming (Buddy)
  Warning: 06:30 PM conflict - Play session (Whiskers) and Brush fur (Whiskers)

Completing Breakfast (daily):
  Next Breakfast is due [tomorrow's date]
  Whiskers now has 3 tasks
```
