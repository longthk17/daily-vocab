"""Collect vocabulary words in a JSON file from the terminal."""

import json
import re
from datetime import date
from functools import lru_cache
from pathlib import Path

from spellchecker import SpellChecker  # type: ignore[import-untyped]

DATA_FILE = Path(__file__).resolve().with_name("vocabulary.json")
REVIEW_FILE = Path(__file__).resolve().with_name("reviews.json")


class DuplicateWordError(ValueError):
    """Raised when a word is already in the vocabulary."""


class SpellingError(ValueError):
    """Raised when an entry contains an unrecognized English word."""


@lru_cache(maxsize=1)
def english_dictionary() -> SpellChecker:
    return SpellChecker(language="en")


def check_spelling(word: str) -> None:
    """Check words and short phrases without silently correcting the input."""
    normalized = word.replace("\u2019", "'")
    if not re.fullmatch(
        r"[A-Za-z]+(?:'[A-Za-z]+)*(?:[ -][A-Za-z]+(?:'[A-Za-z]+)*)*", normalized
    ):
        raise SpellingError(
            "Enter English words using letters, spaces, apostrophes, or hyphens."
        )

    spell = english_dictionary()
    problems = []
    for token in re.split(r"[ -]", normalized.casefold()):
        if not spell.known([token]):
            suggestion = spell.correction(token)
            message = f"Unrecognized word: {token!r}."
            if suggestion:
                message += f" Did you mean {suggestion!r}?"
            problems.append(message)
    if problems:
        raise SpellingError(" ".join(problems))


def load_words(data_file: Path = DATA_FILE) -> list[str]:
    words = []
    if data_file.exists():
        words = json.loads(data_file.read_text(encoding="utf-8"))
        if not isinstance(words, list) or not all(
            isinstance(item, str) for item in words
        ):
            raise ValueError("Vocabulary JSON must contain a list of strings.")
    return words


def add_word(word: str, data_file: Path = DATA_FILE) -> None:
    word = word.strip()
    if not word:
        raise ValueError("The word cannot be empty.")
    words = load_words(data_file)

    if any(existing.strip().casefold() == word.casefold() for existing in words):
        message = f"Duplicate word: {word!r} is already in your vocabulary."
        print(f"WARNING: {message}", flush=True)
        raise DuplicateWordError(message)

    check_spelling(word)
    words.append(word)
    data_file.write_text(
        json.dumps(words, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def new_words() -> None:
    print("Enter one word or phrase at a time. Enter /back to return to the menu.")
    while True:
        word = input("New word: ").strip()
        if word.casefold() == "/back":
            return

        if not word:
            print("Please enter a word.")
            continue

        try:
            add_word(word)
        except (ValueError, OSError) as error:
            print(f"Not saved: {error}")
            continue
        print("Spelling check passed.")
        print(f"Saved: {word}")


def load_reviews(review_file: Path = REVIEW_FILE) -> dict[str, str]:
    if not review_file.exists():
        return {}
    reviews = json.loads(review_file.read_text(encoding="utf-8"))
    if not isinstance(reviews, dict):
        raise ValueError(
            "Review JSON must contain an object of words and review dates."
        )
    for value in reviews.values():
        if not isinstance(value, str):
            raise ValueError("Review dates must be ISO date strings.")
        date.fromisoformat(value)
    return reviews


def remove_word(
    word: str, data_file: Path = DATA_FILE, review_file: Path = REVIEW_FILE
) -> None:
    key = word.strip().casefold()
    if not key:
        raise ValueError("The word cannot be empty.")
    words = load_words(data_file)
    remaining = [item for item in words if item.strip().casefold() != key]
    if len(remaining) == len(words):
        raise ValueError(f"Word not found: {word.strip()!r}.")
    reviews = load_reviews(review_file)
    # Clean history first so a file-access failure leaves the word available to retry.
    if key in reviews:
        del reviews[key]
        review_file.write_text(
            json.dumps(reviews, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    data_file.write_text(
        json.dumps(remaining, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def remove_words() -> None:
    print("Enter a word or phrase to remove. Enter /back to return to the menu.")
    while True:
        word = input("Remove word: ").strip()
        if word.casefold() == "/back":
            return
        try:
            remove_word(word)
        except (ValueError, OSError) as error:
            print(f"Not removed: {error}")
            continue
        print(f"Removed: {word}")


def daily_review(
    data_file: Path = DATA_FILE,
    review_file: Path = REVIEW_FILE,
    today: date | None = None,
) -> None:
    words = load_words(data_file)
    if not words:
        print("No vocabulary yet. Add some words first.")
        return
    reviews = load_reviews(review_file)

    today_string = (today or date.today()).isoformat()
    # Deduplicate legacy entries while preserving their original spelling and order.
    unique: dict[str, str] = {}
    for word in words:
        if word.strip():
            unique.setdefault(word.strip().casefold(), word)
    ordered = list(unique.values())
    due = [
        word
        for word in ordered
        if reviews.get(word.strip().casefold(), "") < today_string
    ]
    due.sort(key=lambda word: reviews.get(word.strip().casefold(), ""))
    due = due[:10]
    if not due:
        print("All saved words have been reviewed today. Come back tomorrow!")
        return

    print("Enter /back at any review prompt to return to the menu.")
    print(
        f"Daily review: {len(due)} words. Recall each word's meaning and use it in a sentence."
    )
    for index, word in enumerate(due, 1):
        print(f"{index}/{len(due)}: {word}")
        while True:
            answer = (
                input("Enter = mark reviewed, s = skip, /back = menu: ")
                .strip()
                .casefold()
            )
            if answer in ("", "s", "b", "/back"):
                break
            print("Choose Enter, s, or /back to return to the menu.")
        if answer in ("b", "/back"):
            return
        if answer == "s":
            continue
        updated = {**reviews, word.strip().casefold(): today_string}
        review_file.write_text(
            json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        reviews = updated
        print("Review saved.")
    print("Review session finished. Choose Daily review again for more words.")


def main() -> None:
    print("Vocabulary learning. Press Ctrl+C to quit.")
    while True:
        try:
            print("\n1. Add new words\n2. Daily review\n3. Remove a word\n0. Exit")
            print("Inside any option, enter /back to return to this menu.")
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Goodbye!")
                return
            if choice == "1":
                new_words()
            elif choice == "2":
                daily_review()
            elif choice == "3":
                remove_words()
            else:
                print("Please choose 1, 2, 3, or 0.")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return
        except (ValueError, OSError) as error:
            print(f"Unable to complete the action: {error}")


if __name__ == "__main__":
    main()
