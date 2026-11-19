# Security+ Acronym Quiz

A command-line flashcard quiz for practicing cybersecurity acronyms and the
terminology commonly encountered in the CompTIA Security+ SY0-701 objectives.

The quiz uses a comprehensive JSON word list, presents meaningful multiple-choice
answers, and automatically brings difficult cards back in future rounds.

## Highlights

- 200+ cybersecurity acronyms
- 15 randomly selected questions per default round
- Three quiz modes:
  - `mixed` — alternates between expansion and scenario questions
  - `expansion` — choose the correct full form of an acronym
  - `scenario` — choose the acronym that best fits a situation
- Plausible, acronym-fitting distractors instead of unrelated answers
- Explanations after correct and incorrect answers
- German descriptions (`Notiz`) for every entry
- Persistent review queue for difficult acronyms
- First-attempt grading at the end of every round
- No external Python packages required

## Requirements

- Python 3.10 or newer

## Quick Start

```bash
git clone <repository-url>
cd <repository-directory>
python3 quiz.py
```

The default mode is `mixed`, with 15 questions per round.

## Example

```text
Question 1/15: Situation: An organization needs a control point that enforces
policy between its employees and multiple SaaS providers.
Which acronym best fits this situation?
Category: Cloud & Network
  A) DLP
  B) CASB
  C) HSM
  D) SIEM

Your answer (A-D, or Q to quit):
```

Wrong answers are eliminated, and the German explanation is displayed before
the next attempt. After a correct answer, the full expansion and explanation
are shown again.

## Quiz Modes

### Mixed

```bash
python3 quiz.py
# or explicitly:
python3 quiz.py --mode mixed
```

Randomly alternates between expansion and scenario questions.

### Expansion

```bash
python3 quiz.py --mode expansion
```

Given an acronym, choose its correct full expansion. Incorrect options are
believable alternatives whose words still match the acronym.

### Scenario

```bash
python3 quiz.py --mode scenario
```

Read a situational description and select the acronym that best fits. Choosing
an incorrect acronym displays its full expansion and explains that it does not
address the described situation.

## Options

```text
usage: quiz.py [-h] [-n QUESTIONS] [--list LIST_PATH] [--state STATE_PATH]
               [--reset-progress] [--seed SEED]
               [--mode {mixed,expansion,scenario}]
```

Common examples:

```bash
# Short five-question mixed round
python3 quiz.py -n 5

# Scenario-only round
python3 quiz.py --mode scenario

# Expansion round from another word list
python3 quiz.py --list path/to/custom-list.json --mode expansion

# Reproducible order for demonstrations or classes
python3 quiz.py --seed 42

# Reset saved review cards
python3 quiz.py --reset-progress
```

Use `Q` during a round to stop.

## Review-Card Behavior

The quiz works like a simple cue-card system:

1. The user may retry after a wrong choice.
2. If an acronym requires at least two wrong attempts before being answered,
   it is added to the review queue.
3. Acronyms in the review queue are prioritized in the next round.
4. The queue is saved in `.quiz_progress.json`.

The state file is created next to the script by default. Use `--state` to store
it elsewhere:

```bash
python3 quiz.py --state .progress/my-class.json
```

## Acronym Data

Quiz entries are stored in [`List.json`](List.json). Each entry contains:

```json
{
  "acronym": "SIEM",
  "full_name": "Security Information and Event Management",
  "category": "Monitoring & Operations",
  "description": "Zentrales System zur Sammlung, Korrelation und Analyse von Logdaten in Echtzeit."
}
```

Requirements for custom list entries:

- `acronym`, `full_name`, `category`, and `description` must be non-empty strings.
- Acronym values must be unique.
- The list must contain at least four entries.
- Use concise descriptions that help explain the concept.

The scenario and curated expansion logic also lives in [`quiz.py`](quiz.py).
New entries automatically receive generated scenario and expansion distractors;
entries without handcrafted situations use the German `description` as their
scenario prompt.

## Running the Tests

```bash
python3 -m unittest -v
```

The tests validate data loading, choice generation, scenario feedback, review
queue persistence, and review prioritization.

## Exam Scope

This project is a study aid, not an official CompTIA resource and not a
guarantee of complete exam coverage. The list is designed around the terminology
associated with Security+ SY0-701, but candidates should also practice:

- performance-based questions
- command-line and configuration tasks
- log and indicator analysis
- architecture and scenario reasoning
- the current official CompTIA exam objectives

CompTIA product names and exam codes belong to their respective owners.

## Contributing

Contributions are welcome:

1. Add or correct entries in `List.json`.
2. Keep expansions accurate and descriptions concise.
3. Add a believable German description.
4. Run `python3 -m unittest -v`.
5. Open a pull request describing the source and reason for the change.

Useful contributions include:

- terminology corrections
- additional scenario questions
- translation improvements
- accessibility and terminal UX improvements
- test coverage

## Disclaimer

Use this quiz for lawful, authorized study and training. Accuracy matters in
certification material: when reporting an error, include a trustworthy reference
or a clear explanation of the correction.
