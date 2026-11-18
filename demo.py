"""Prints sample chat interactions so you can see PawPal work without opening the app.

Run:  python demo.py
"""

from datetime import date

from pawpal_system import Owner
from rag import reply

owner = Owner("Jordan")
today = date(2026, 11, 17)  # the day selected on the calendar

messages = [
    "add a dog named Buddy and put him on the schedule for a walk on nov 20th at 8am",
    "add a cat named Mochi",
    "build a routine for Mochi on nov 18",
    "what is Buddy doing on nov 20?",
    "what should I feed my cat?",
    "quantum physics",
]

for message in messages:
    text, added = reply(message, owner, today)
    print(f"You:    {message}")
    print(f"PawPal: {text}\n")
