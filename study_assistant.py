#!/usr/bin/env python3
"""
AI Student Study Assistant
==========================
A command-line study companion that helps students learn smarter:

  * Flashcards with spaced repetition (Leitner box system)
  * Multiple-choice quizzes generated from your own flashcards
  * Exam study planner that spreads topics across the days left
  * Pomodoro focus timer that logs your study time
  * Progress statistics

All data is stored locally in study_data.json. No external libraries needed.

Usage examples:
    python study_assistant.py add --topic Python --question "What is a list?" --answer "An ordered, mutable collection"
    python study_assistant.py review
    python study_assistant.py quiz --topic Python --num 5
    python study_assistant.py plan --exam 2026-11-20 --topics "Arrays,Loops,Functions,OOP" --hours 2
    python study_assistant.py timer --work 25 --rest 5 --rounds 2
    python study_assistant.py stats
"""

import argparse
import json
import random
import time
from datetime import date, timedelta
from pathlib import Path

DATA_FILE = Path("study_data.json")

# Leitner system: box number -> days until the card is shown again
BOX_INTERVALS = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}


# ---------------------------------------------------------------- storage
def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"cards": [], "sessions": []}


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# -------------------------------------------------------------- flashcards
def cmd_add(args):
    data = load_data()
    next_id = max((c["id"] for c in data["cards"]), default=0) + 1
    data["cards"].append({
        "id": next_id,
        "topic": args.topic,
        "question": args.question,
        "answer": args.answer,
        "box": 1,
        "due": date.today().isoformat(),
        "reviews": 0,
        "correct": 0,
    })
    save_data(data)
    print(f"Added card #{next_id} to topic '{args.topic}'.")


def cmd_list(args):
    data = load_data()
    cards = [c for c in data["cards"] if not args.topic or c["topic"].lower() == args.topic.lower()]
    if not cards:
        print("No cards found.")
        return
    for c in cards:
        print(f"#{c['id']:<3} [{c['topic']}] box {c['box']} due {c['due']}  Q: {c['question']}")


def cmd_review(args):
    """Review cards that are due today, moving them between Leitner boxes."""
    data = load_data()
    today = date.today().isoformat()
    due = [c for c in data["cards"]
           if c["due"] <= today and (not args.topic or c["topic"].lower() == args.topic.lower())]
    if not due:
        print("Nothing due today. Great job staying on top of it!")
        return
    random.shuffle(due)
    print(f"{len(due)} card(s) due. Press Enter to reveal each answer.\n")
    right = 0
    for card in due:
        print(f"[{card['topic']}] Q: {card['question']}")
        input("   (press Enter to show answer) ")
        print(f"   A: {card['answer']}")
        got_it = input("   Did you get it right? (y/n): ").strip().lower() == "y"
        card["reviews"] += 1
        if got_it:
            card["correct"] += 1
            right += 1
            card["box"] = min(card["box"] + 1, 5)
        else:
            card["box"] = 1
        card["due"] = (date.today() + timedelta(days=BOX_INTERVALS[card["box"]])).isoformat()
        print()
    save_data(data)
    print(f"Session complete: {right}/{len(due)} correct.")


# -------------------------------------------------------------------- quiz
def cmd_quiz(args):
    """Multiple-choice quiz built from existing flashcards."""
    data = load_data()
    pool = [c for c in data["cards"] if not args.topic or c["topic"].lower() == args.topic.lower()]
    if len(pool) < 4:
        print("You need at least 4 flashcards (in that topic) to build a quiz.")
        return
    questions = random.sample(pool, min(args.num, len(pool)))
    score = 0
    for i, card in enumerate(questions, 1):
        wrong = random.sample([c["answer"] for c in pool if c["id"] != card["id"]], 3)
        options = wrong + [card["answer"]]
        random.shuffle(options)
        print(f"Q{i}. {card['question']}")
        for letter, option in zip("ABCD", options):
            print(f"   {letter}) {option}")
        choice = input("   Your answer (A-D): ").strip().upper()
        picked = options["ABCD".index(choice)] if choice in list("ABCD") else None
        if picked == card["answer"]:
            print("   Correct!\n")
            score += 1
        else:
            print(f"   Not quite. Correct answer: {card['answer']}\n")
    print(f"Final score: {score}/{len(questions)} ({round(100 * score / len(questions))}%)")


# ----------------------------------------------------------------- planner
def cmd_plan(args):
    """Spread topics over the days until the exam, keeping the last days for revision."""
    exam = date.fromisoformat(args.exam)
    days_left = (exam - date.today()).days
    topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    if days_left < 1:
        print("The exam date must be in the future.")
        return
    if not topics:
        print("Please give at least one topic.")
        return
    revision_days = min(2, max(days_left - len(topics), 0))
    learning_days = days_left - revision_days
    print(f"Study plan: {days_left} day(s) until {exam:%d %b %Y}, {args.hours} h/day\n")
    for d in range(days_left):
        day = date.today() + timedelta(days=d)
        if d < learning_days:
            topic = topics[min(int(d * len(topics) / learning_days), len(topics) - 1)]
            task = f"Learn + practice: {topic}"
        else:
            task = "Full revision + mock test"
        print(f"{day:%a %d %b}  |  {args.hours} h  |  {task}")


# ------------------------------------------------------------------- timer
def cmd_timer(args):
    """Pomodoro timer: work/rest rounds, logged to your stats."""
    data = load_data()
    for r in range(1, args.rounds + 1):
        print(f"Round {r}/{args.rounds}: focus for {args.work} min. Stay on task!")
        time.sleep(args.work * 60)
        data["sessions"].append({"date": date.today().isoformat(), "minutes": args.work})
        save_data(data)
        if r < args.rounds:
            print(f"Break time: relax for {args.rest} min.")
            time.sleep(args.rest * 60)
    print("All rounds done. Well done!")


# ------------------------------------------------------------------- stats
def cmd_stats(args):
    data = load_data()
    cards, sessions = data["cards"], data["sessions"]
    reviews = sum(c["reviews"] for c in cards)
    correct = sum(c["correct"] for c in cards)
    accuracy = round(100 * correct / reviews) if reviews else 0
    minutes = sum(s["minutes"] for s in sessions)
    print("=== Study Progress ===")
    print(f"Flashcards      : {len(cards)}")
    print(f"Reviews done    : {reviews} (accuracy {accuracy}%)")
    print(f"Focus time      : {minutes} min ({minutes / 60:.1f} h)")
    print("Cards per box   : " + ", ".join(
        f"Box {b}: {sum(1 for c in cards if c['box'] == b)}" for b in BOX_INTERVALS))
    mastered = sum(1 for c in cards if c["box"] == 5)
    print(f"Mastered (box 5): {mastered}")


# --------------------------------------------------------------------- CLI
def build_parser():
    p = argparse.ArgumentParser(description="AI Student Study Assistant")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add", help="add a flashcard")
    a.add_argument("--topic", required=True)
    a.add_argument("--question", required=True)
    a.add_argument("--answer", required=True)
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list", help="list flashcards")
    l.add_argument("--topic")
    l.set_defaults(func=cmd_list)

    r = sub.add_parser("review", help="review cards due today")
    r.add_argument("--topic")
    r.set_defaults(func=cmd_review)

    q = sub.add_parser("quiz", help="multiple-choice quiz from flashcards")
    q.add_argument("--topic")
    q.add_argument("--num", type=int, default=5)
    q.set_defaults(func=cmd_quiz)

    pl = sub.add_parser("plan", help="generate an exam study plan")
    pl.add_argument("--exam", required=True, help="exam date, YYYY-MM-DD")
    pl.add_argument("--topics", required=True, help="comma-separated topics")
    pl.add_argument("--hours", type=float, default=2, help="study hours per day")
    pl.set_defaults(func=cmd_plan)

    t = sub.add_parser("timer", help="Pomodoro focus timer")
    t.add_argument("--work", type=int, default=25)
    t.add_argument("--rest", type=int, default=5)
    t.add_argument("--rounds", type=int, default=4)
    t.set_defaults(func=cmd_timer)

    s = sub.add_parser("stats", help="show your progress")
    s.set_defaults(func=cmd_stats)
    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
