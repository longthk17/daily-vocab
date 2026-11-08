# Vocabulary program specification

## Purpose

Build a Python terminal application for collecting vocabulary words. This file defines the requirements used to implement the application and future changes.

## Current requirements

- The user types one new word at a time in the terminal.
- Save each accepted word immediately to a JSON file.
- Check for duplicates before saving.
- Check English spelling before saving; reject unrecognized words and suggest a correction when available.
- When a duplicate is found, print a warning and continue prompting without saving.

## Environment and files

- Application files live together in `vocabulary/` in the source repository, or at the root after extraction into a standalone repository. See `AGENTS.md` for migration and handoff instructions.
- Use the existing repository-root `.venv` Python environment. Its Command Prompt activation file is `.venv\Scripts\activate.bat` from the repository root.
- Application entry point: `vocabulary/vocabulary.py` from the repository root.
- Run from the repository root with `.venv\Scripts\python.exe vocabulary\vocabulary.py`.
- Data file: `vocabulary.json`, beside the application regardless of the terminal's current directory.
- Install the spelling dictionary dependency from the repository root with `.venv\Scripts\python.exe -m pip install -r vocabulary\requirements.txt`.
- Spelling checks use pyspellchecker locally; no internet connection is required after installation.
- After extraction, create a new `.venv`, install with `.venv\Scripts\python.exe -m pip install -r requirements.txt`, and run `.venv\Scripts\python.exe vocabulary.py` from the new repository root.

## Input behavior

- Start with a menu: `1` to add new words, `2` for daily review, `3` to remove a word, `0` to exit.
- In new-word mode, enter `/back` to return to the menu.
- Prompt repeatedly for a new word.
- Remove leading and trailing whitespace before checking or saving.
- For blank input, display a message and prompt again without saving.
- Preserve accepted spelling and letter case in storage.
- Exit cleanly on Ctrl+C or end-of-input.
- Accept individual English words and short phrases, with apostrophes and hyphens.
- For unrecognized spellings, display a message and prompt again without saving.
- Dictionary checks can reject names or uncommon words. They do not check grammar or whether a correctly spelled word fits a sentence.

## JSON storage

- Store words as a UTF-8 JSON array of strings.
- Create the file when the first valid word is saved if it does not exist.
- Preserve existing words and append new words in entry order.
- Save each word before displaying a success message.
- Load stored words for duplicate checking, including after restarting.
- Raise an error for invalid existing JSON or data that is not an array of strings, without overwriting it.

Example data:

```json
[
  "apple",
  "banana"
]
```

## Duplicate handling

- Compare words without regard to letter case or surrounding whitespace.
- Treat `Apple`, `apple`, and ` apple ` as duplicates.
- Print a warning identifying the duplicate word.
- Raise `DuplicateWordError`, a subclass of `ValueError`.
- Leave the JSON file unchanged when rejecting a duplicate.
- Catch validation and file-access errors in the terminal loop, display a message, and continue prompting without a traceback.

## Acceptance criteria

1. A new word is saved and a success message is displayed.
2. A second distinct word is appended without losing existing entries.
3. An existing word, including case or surrounding-whitespace variations, triggers a warning and `DuplicateWordError`.
4. A rejected duplicate does not change the JSON file.
5. Duplicate detection still works after restarting the application.
6. Blank input does not create an entry.
7. Invalid existing data is reported and preserved.

## Initial scope limits

Definitions, translations, quizzes, editing, and concurrent application instances are outside the initial scope.

## Remove words

- Option `3` prompts repeatedly for a word or phrase to remove; `/back` returns to the menu.
- Match without regard to case or surrounding whitespace and remove all matching entries.
- Remove the word's review history so adding it again starts fresh.
- Blank input, missing words, invalid data, and file-access errors display a message without crashing.

## Daily review

- Suggest up to 10 saved words per session, prioritizing never-reviewed words, then the least recently reviewed.
- Use the computer's local calendar date. Exclude words already marked reviewed today.
- Display each word and ask the learner to recall its meaning and use it in a sentence.
- Press Enter to mark reviewed, `s` to skip, or `/back` to return to the menu (`b` also works).
- Every menu option displays the `/back` instruction.
- Save each completed review immediately in `reviews.json` beside the application, mapping words to ISO review dates.
- Keep the existing vocabulary JSON array unchanged. Preserve invalid review data and report an error without crashing.
- Reopening daily review offers more eligible words. Previously reviewed words become eligible again the next day.
- Reviews are offered when running the app; there are no background notifications.
