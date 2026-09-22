"""Chapters 03-04: control flow and the built-in collections.

Implement every function so that tests/test_02_control_and_collections.py passes.
"""

from collections.abc import Iterable, Sequence


def grade(score: int) -> str:
    """(basic) Map a score to a grade: >=90 "A", >=75 "B", >=60 "C", otherwise "F".

    Raise ValueError if the score is outside 0..100.
    """
    raise NotImplementedError


def parse_command(command: str) -> tuple[str, list[str]]:
    """(thinking) Split a command line into an action and its arguments.

    Use a ``match`` statement. The rules:

    - "quit"                -> ("quit", [])
    - "load report.csv"     -> ("load", ["report.csv"])
    - "save out.csv --force"-> ("save", ["out.csv", "--force"])
    - an empty string       -> ValueError
    - an unknown action     -> ValueError with the action name in the message

    Known actions: quit, load, save.
    """
    raise NotImplementedError


def first_matching(items: Sequence[int], threshold: int) -> int:
    """(thinking) Return the first element greater than ``threshold``.

    Raise ``LookupError("no element above threshold")`` if there is none.
    Write it with a ``for ... else`` construct - no flag variable.
    """
    raise NotImplementedError


def unique_preserving_order(items: Iterable[str]) -> list[str]:
    """(junior interview) Remove duplicates while keeping first-seen order.

    >>> unique_preserving_order(["b", "a", "b", "c", "a"])
    ['b', 'a', 'c']
    """
    raise NotImplementedError


def word_frequencies(text: str) -> dict[str, int]:
    """(basic) Count words case-insensitively.

    Words are whitespace-separated; strip the characters ``.,!?;:`` from both ends.
    Empty tokens are ignored.

    >>> word_frequencies("The cat, the CAT!")
    {'the': 2, 'cat': 2}
    """
    raise NotImplementedError


def top_n(counts: dict[str, int], n: int) -> list[tuple[str, int]]:
    """(thinking) The ``n`` most frequent entries, highest count first.

    Ties are broken alphabetically by key.

    >>> top_n({"b": 2, "a": 2, "c": 1}, 2)
    [('a', 2), ('b', 2)]
    """
    raise NotImplementedError


def group_by_first_letter(names: Iterable[str]) -> dict[str, list[str]]:
    """(basic) Group names by their upper-cased first letter, order preserved.

    >>> group_by_first_letter(["anna", "bob", "alex"])
    {'A': ['anna', 'alex'], 'B': ['bob']}
    """
    raise NotImplementedError


def missing_fields(required: Iterable[str], record: dict[str, object]) -> set[str]:
    """(basic) Which required fields are absent from the record?

    A key present with a value of None counts as missing.
    """
    raise NotImplementedError


def merge_configs(defaults: dict[str, object], overrides: dict[str, object]) -> dict[str, object]:
    """(basic) Merge two configuration dicts; ``overrides`` wins.

    Neither input may be modified.
    """
    raise NotImplementedError


def chunk(items: Sequence[int], size: int) -> list[list[int]]:
    """(thinking) Split a sequence into consecutive chunks of at most ``size``.

    Raise ValueError if ``size`` is not positive.

    >>> chunk([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    """
    raise NotImplementedError


def last_n_events(events: Iterable[str], n: int) -> list[str]:
    """(thinking) Keep only the last ``n`` events from a potentially endless stream.

    Memory use must not grow with the number of events - use the right collection
    from the standard library rather than building a full list.
    """
    raise NotImplementedError
