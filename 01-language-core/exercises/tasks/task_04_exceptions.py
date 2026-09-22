"""Chapter 07: exceptions and error handling.

Implement everything so that tests/test_04_exceptions.py passes.
"""

from collections.abc import Callable, Iterable
from decimal import Decimal

# --- 1. (basic) Define the exception hierarchy -------------------------------
#
# Replace the three placeholder assignments below with real class definitions.
#
#   ImportFailure      - base class for everything this module raises
#   ValidationError    - a single field failed validation; carries `field` and
#                        `reason` attributes, and its str() is "field: reason"
#   SourceUnavailable  - the input could not be read at all
#
# Requirement: `except ImportFailure` must catch both of the others.

ImportFailure = NotImplemented
ValidationError = NotImplemented
SourceUnavailable = NotImplemented


def parse_amount(text: str) -> Decimal:
    """(basic) Parse a decimal amount.

    Raise ``ValidationError("amount", ...)`` when the text is not a number or the
    value is negative. Keep the original exception as the cause (``raise ... from``).
    """
    raise NotImplementedError


def dig(data: dict[str, object], *keys: str) -> object | None:
    """(thinking) Walk a nested dictionary, returning None if any step is missing.

    >>> dig({"a": {"b": {"c": 1}}}, "a", "b", "c")
    1
    >>> dig({"a": {}}, "a", "b", "c") is None
    True

    Write it in EAFP style: try the lookups, catch what goes wrong. It must also
    survive hitting a non-dict value halfway down.
    """
    raise NotImplementedError


def retry(operation: Callable[[], str], attempts: int = 3) -> str:
    """(junior interview) Call ``operation`` until it succeeds.

    On failure, retry up to ``attempts`` times in total. If every attempt fails,
    raise ``SourceUnavailable`` chained from the last error (``from``), with the
    number of attempts in the message.

    Only ``OSError`` (and its subclasses) counts as retriable - anything else
    propagates immediately.
    """
    raise NotImplementedError


def process_records(
    records: Iterable[dict[str, str]],
) -> tuple[list[Decimal], list[str]]:
    """(thinking) Parse the "amount" of every record; never abort on a bad one.

    Returns (parsed amounts, error messages). One bad record must not kill the
    batch - collect the message as ``"row {n}: {error}"`` (1-based) and carry on.
    A record without an "amount" key is an error too.
    """
    raise NotImplementedError


def load_settings(path: str, defaults: dict[str, str]) -> dict[str, str]:
    """(basic) Read ``key=value`` lines from a file, falling back to defaults.

    - Missing file: return the defaults unchanged (do not raise).
    - Unreadable file (permissions): let the error propagate.
    - Blank lines and ``#`` comments are ignored.
    - Values from the file override the defaults.
    """
    raise NotImplementedError
