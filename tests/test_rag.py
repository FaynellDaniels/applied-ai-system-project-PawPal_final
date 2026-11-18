from datetime import date

from pawpal_system import Owner, Pet, Scheduler
from rag import find_day, reply, retrieve

DAY = date(2026, 1, 5)


def make_owner():
    return Owner("Jordan", [Pet("Buddy", "dog"), Pet("Mochi", "cat")])


def test_retrieve_matches_species():
    assert retrieve("litter box", "cat")[0]["id"] == "cat_litter"
    assert retrieve("litter box", "dog") == []


def test_answer_uses_retrieved_tip():
    text, added = reply("what should I feed my cat?", make_owner(), DAY)
    assert "Mochi" in text and "Buddy" not in text and added == []


def test_routine_adds_tasks_with_no_conflicts():
    owner = make_owner()
    _, added = reply("build a routine for my dog and cat", owner, DAY)
    assert len(added) == 8
    assert Scheduler(owner).find_conflicts() == []


def test_add_task_with_time():
    owner = make_owner()
    _, added = reply("add a walk for Buddy at 5pm", owner, DAY)
    assert added[0].due_time.hour == 17


def test_routine_twice_does_not_duplicate():
    owner = make_owner()
    reply("routine for Buddy", owner, DAY)
    _, added = reply("routine for Buddy", owner, DAY)
    assert added == []


def test_empty_message_and_no_pets_and_unknown_topic():
    assert reply("", make_owner(), DAY)[1] == []
    assert "Add a pet" in reply("hi", Owner("X"), DAY)[0]
    assert "don't know" in reply("quantum physics", make_owner(), DAY)[0]


def test_chat_knows_what_each_pet_is_doing():
    owner = make_owner()
    reply("build a routine for my dog today", owner, DAY)
    text, _ = reply("what is Buddy doing today?", owner, DAY)
    assert "Breakfast" in text and "Morning walk" in text and "Mochi" not in text


def test_chat_says_when_nothing_is_planned():
    text, _ = reply("what is Mochi doing?", make_owner(), DAY)
    assert "nothing" in text


def test_add_task_to_a_chosen_day():
    owner = make_owner()
    _, added = reply("add a walk for Buddy at 5pm on nov 20", owner, DAY)
    assert added[0].due_date.month == 11 and added[0].due_date.day == 20


def test_find_day():
    today = date(2026, 11, 17)  # a Tuesday
    assert find_day("walk tomorrow", DAY, today) == date(2026, 11, 18)
    assert find_day("walk on friday", DAY, today) == date(2026, 11, 20)
    assert find_day("walk", DAY, today) == DAY


def test_hello():
    assert "Woof" in reply("hi", make_owner(), DAY)[0]


def test_chat_adds_a_new_pet_and_schedules_a_walk():
    owner = Owner("Jordan")  # no pets yet
    text, added = reply("add a dog named buddy and put him on the schedule for a walk on nov 20th at 8am", owner, DAY)
    assert [(p.name, p.species) for p in owner.pets] == [("Buddy", "dog")]
    walk = owner.pets[0].tasks[0]
    assert (walk.due_date.month, walk.due_date.day, walk.due_time.hour) == (11, 20, 8)
    assert "Added **Buddy**" in text and added == [walk]


def test_chat_adds_a_pet_without_any_task():
    owner = make_owner()
    text, added = reply("I got a new kitten called Luna", owner, DAY)
    assert owner.pets[-1].name == "Luna" and owner.pets[-1].species == "cat"
    assert added == [] and "routine" in text


def test_chat_does_not_duplicate_an_existing_pet():
    owner = make_owner()
    reply("add a dog named Buddy", owner, DAY)
    assert len(owner.pets) == 2


def test_chat_can_add_a_bunny_as_other():
    owner = Owner("Jordan")
    reply("add a bunny named Clover and build a routine", owner, DAY)
    assert owner.pets[0].species == "other" and owner.pets[0].tasks
