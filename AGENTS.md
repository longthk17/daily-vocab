# Vocabulary application handoff

## Project and user intent

This is a Python terminal application for collecting English vocabulary and reviewing it daily. It is being extracted from `learn-python` into its own repository. The suggested repository name is `daily-vocab`; the user has not confirmed the name or requested creation of a remote repository.

Read `vocabulary.md` for the detailed requirements and `vocabulary.py` for the implementation. Keep this document and the specification current when behavior changes.

## Layout and setup

All application files live beside this document. In the source repository they are under `vocabulary/`; in the standalone repository they should be at the repository root.

- `vocabulary.py`: entry point and application logic.
- `requirements.txt`: application dependency, `pyspellchecker==0.9.0`. Do not copy the parent repository's unrelated dependencies.
- `vocabulary.md`: behavior specification.
- `vocabulary.json`: live user words, stored as a UTF-8 JSON array of strings.
- `reviews.json`: live review history, an object mapping normalized words to ISO date strings.
- `vocabulary.txt`: legacy word list, retained for reference; the program does not import it automatically.

From the standalone repository root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe vocabulary.py
```

Before extraction, use the parent repository's `.venv` and run `vocabulary/vocabulary.py` from that repository root. Storage paths are derived from `__file__`, so they continue to work after moving the application or launching it from another directory.

## Required behavior

- Menu: `1` add new words, `2` daily review, `3` remove a word, `0` exit.
- Every mode must display and support `/back` to return to the main menu. Commands ignore case and surrounding whitespace.
- User preference: validation and file-access errors must display a useful message and allow continued use, without a traceback or process crash. Ctrl+C and EOF exit cleanly.
- Adding: trim input, reject blanks and duplicates, check English spelling, preserve accepted spelling/case, save immediately. Duplicate comparison ignores case and surrounding whitespace. Suggest corrections for unknown words without saving or silently replacing them.
- Spelling uses a local pyspellchecker dictionary after installation. Words and short phrases can contain letters, apostrophes, and hyphens. This does not validate grammar or contextual word choice; uncommon words and names may be rejected.
- Review: offer up to 10 words per session, never-reviewed first, then least recently reviewed. Exclude words reviewed on or after the local current date. Enter marks reviewed immediately, `s` skips, `/back` returns (`b` is also supported). Another session can offer more eligible words the same day. Words become eligible again the next day. No background reminders or automatic grading.
- Removal: match case-insensitively after trimming, delete all matching vocabulary entries and the normalized word's review history. Keep prompting on blanks, missing words, or errors. Removing and re-adding a word resets its review history.
- Preserve invalid existing JSON and report it; never reset it to an empty collection automatically.
- Definitions, translations, quizzes, editing, and concurrent instances are not implemented.

## Migration and data preservation

Copy this directory's source, requirements, specification, and AGENTS.md into the new repository root. Transfer `vocabulary.json`, `reviews.json`, and the legacy `vocabulary.txt` locally so the user's learning progress is retained. Do not copy `.venv`, `__pycache__`, or the parent `.git` directory. Create a fresh virtual environment and ignore `.venv/` and `__pycache__/` in the new repository.

The JSON files contain real user data. Preserve them during development and migration, and keep them out of commits to a public repository by default. Add `vocabulary.json` and `reviews.json` to the new repository's `.gitignore` before staging. Do not remove the original directory until the new copy has been verified. Creating or publishing a remote repository is a separate action that has not yet been requested.

## Verification and known limitations

There is no committed automated test suite yet. Previous checks used temporary directories and mocked terminal input; do not run checks against live user JSON files.

For functional changes, verify the affected behavior and relevant persistence: add/duplicate/spelling rejection, all menu routes and `/back`, removal/history cleanup, review skipping and 10-word limit, same-day exclusion and next-day eligibility, malformed JSON preservation, and continued operation after expected errors.

Removal updates review history before the vocabulary file. The two writes are not transactional: if the vocabulary write fails after history cleanup, the word remains but its review date may be lost. Concurrent processes and atomic multi-file writes are not supported.
