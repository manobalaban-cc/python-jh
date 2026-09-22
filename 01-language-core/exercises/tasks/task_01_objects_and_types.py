"""Chapters 01-02: object model, references, mutability, numbers, strings.

Implement every function so that tests/test_01_objects_and_types.py passes.
"""

from decimal import Decimal


def append_without_mutating(items: list[int], value: int) -> list[int]:
    """(basic) Return a NEW list with ``value`` appended, leaving ``items`` untouched.

    >>> original = [1, 2]
    >>> append_without_mutating(original, 3)
    [1, 2, 3]
    >>> original
    [1, 2]
    """
    raise NotImplementedError


def deep_update(matrix: list[list[int]], row: int, col: int, value: int) -> list[list[int]]:
    """(thinking) Return a copy of ``matrix`` with one cell changed.

    The original matrix - including its inner lists - must not change.

    >>> m = [[1, 2], [3, 4]]
    >>> deep_update(m, 0, 1, 99)
    [[1, 99], [3, 4]]
    >>> m
    [[1, 2], [3, 4]]
    """
    raise NotImplementedError


def are_same_object(a: object, b: object) -> bool:
    """(basic) True if ``a`` and ``b`` are the very same object, not merely equal."""
    raise NotImplementedError


def safe_divide(a: int, b: int) -> float | None:
    """(basic) Return ``a / b`` as a float, or None if ``b`` is zero.

    Use exception handling, not an ``if b == 0`` check (EAFP).
    """
    raise NotImplementedError


def floor_and_remainder(a: int, b: int) -> tuple[int, int]:
    """(thinking) Return the floor division and the remainder of ``a`` by ``b``.

    Watch out for negative operands - Python does not behave like Java here.

    >>> floor_and_remainder(-7, 2)
    (-4, 1)
    """
    raise NotImplementedError


def total_with_vat(prices: list[str], vat_rate: str) -> Decimal:
    """(junior interview) Sum the prices and add VAT, exactly - no floating point error.

    ``prices`` holds decimal strings such as "19.99"; ``vat_rate`` is e.g. "0.27".

    >>> total_with_vat(["19.99", "0.02"], "0.00")
    Decimal('20.01')
    """
    raise NotImplementedError


def normalise_name(raw: str) -> str:
    """(basic) Trim surrounding whitespace, collapse inner runs of whitespace to one
    space, and title-case the result.

    >>> normalise_name("  anna   MARIA  nagy ")
    'Anna Maria Nagy'
    """
    raise NotImplementedError


def initials(full_name: str) -> str:
    """(basic) Return the upper-case initials of each word, separated by dots.

    >>> initials("anna maria nagy")
    'A.M.N.'
    """
    raise NotImplementedError


def format_report_line(name: str, amount: float, share: float) -> str:
    """(thinking) Format one report line, exactly 40 characters wide.

    Layout: the name left-aligned in 20 characters, the amount right-aligned in 12
    characters with a thousands separator and 2 decimals, then the share as a
    percentage with 1 decimal, right-aligned in 8 characters.

    >>> format_report_line("Anna", 1234.5, 0.0873)
    'Anna                    1,234.50    8.7%'
    """
    raise NotImplementedError


def join_lines(lines: list[str]) -> str:
    """(junior interview) Join the lines with newlines, efficiently.

    The point of the exercise: do NOT build the result with ``+=`` in a loop.
    Explain in a comment why that matters.
    """
    raise NotImplementedError


def byte_length(text: str, encoding: str = "utf-8") -> int:
    """(basic) Return how many BYTES ``text`` occupies in the given encoding.

    >>> byte_length("abc")
    3
    >>> byte_length("Grüße")
    7
    """
    raise NotImplementedError
