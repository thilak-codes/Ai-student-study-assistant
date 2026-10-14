# AI Student Study Assistant

A lightweight, dependency-free Python command-line tool that helps students study smarter. It combines **spaced-repetition flashcards**, **auto-generated quizzes**, an **exam study planner**, a **Pomodoro focus timer** and **progress tracking** in a single script.

## Why this project?

Most students re-read notes and cram before exams, which research shows is one of the least effective ways to learn. This tool applies two proven techniques, *active recall* and *spaced repetition*, and adds planning and focus tools so that everything a student needs lives in one place.

## Features

| Feature | What it does |
|---|---|
| Flashcards | Create question/answer cards grouped by topic |
| Spaced repetition | Uses the Leitner box system: right answers move up a box and appear less often, wrong answers return to box 1 |
| Quiz mode | Builds multiple-choice quizzes automatically from your own flashcards |
| Study planner | Splits your topics across the days until the exam and reserves the final days for revision |
| Pomodoro timer | Work/rest cycles, with focus time logged automatically |
| Progress stats | Cards per box, accuracy, mastered cards and total study hours |

## Requirements

- Python 3.8 or newer
- No third-party packages

## Getting started

```bash
git clone https://github.com/<your-username>/ai-student-study-assistant.git
cd ai-student-study-assistant
python study_assistant.py --help
```

## Usage

```bash
# 1. Add flashcards
python study_assistant.py add --topic Python --question "What is a list?" --answer "An ordered, mutable collection"

# 2. List your cards
python study_assistant.py list --topic Python

# 3. Review the cards that are due today
python study_assistant.py review

# 4. Take a multiple-choice quiz (needs at least 4 cards)
python study_assistant.py quiz --topic Python --num 5

# 5. Generate a study plan for an exam
python study_assistant.py plan --exam 2026-11-20 --topics "Arrays,Loops,Functions,OOP" --hours 2

# 6. Start a focus session (2 rounds of 25 min work, 5 min rest)
python study_assistant.py timer --work 25 --rest 5 --rounds 2

# 7. See your progress
python study_assistant.py stats
```

Your data is saved locally in `study_data.json`.

## How the spaced repetition works

| Box | Review again after |
|---|---|
| 1 | 1 day |
| 2 | 2 days |
| 3 | 4 days |
| 4 | 7 days |
| 5 | 14 days (mastered) |

## Project structure

```
ai-student-study-assistant/
├── study_assistant.py   # the whole application
├── README.md
└── study_data.json      # created automatically on first use
```

## Roadmap

- [ ] Import flashcards from CSV or notes
- [ ] Generate flashcards from text using an LLM API
- [ ] Web or GUI front end (Streamlit / Tkinter)
- [ ] Charts for study history
- [ ] Unit tests with `pytest`

## Skills demonstrated

Python, command-line interfaces (`argparse`), JSON data persistence, date/time handling, algorithm design (Leitner scheduling) and clean, documented code.

## License

MIT License. Free to use and modify.
