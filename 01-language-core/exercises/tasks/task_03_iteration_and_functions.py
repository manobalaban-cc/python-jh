"""Chapters 05-06: iteration, comprehensions, generators, functions.

Implement every function so that tests/test_03_iteration_and_functions.py passes.
"""

from collections.abc import Callable, Iterable, Iterator


def active_emails(users: list[dict[str, object]]) -> list[str]:
    """(basic) Lower-cased e-mail addresses of active users, in one comprehension.

    A user is active when ``user["active"]`` is True. Users without an "email" key
    are skipped.
    """
    raise NotImplementedError


def index_by(records: list[dict[str, object]], key: str) -> dict[object, dict[str, object]]:
    """(basic) Build a lookup dict keyed by ``record[key]``. Later records win."""
    raise NotImplementedError


def running_total(values: Iterable[float]) -> Iterator[float]:
    """(thinking) Yield the running total after each value.

    It must be a generator: calling it does no work, and it must cope with an
    infinite input when only the first few values are consumed.

    >>> list(running_total([1, 2, 3]))
    [1, 3, 6]
    """
    raise NotImplementedError


def read_valid_lines(lines: Iterable[str]) -> Iterator[tuple[int, str]]:
    """(thinking) Yield ``(line_number, stripped_line)`` for meaningful lines.

    Line numbering starts at 1 and counts every input line. Skip blank lines and
    lines whose first non-whitespace character is ``#``.
    """
    raise NotImplementedError


def first_error(lines: Iterable[str]) -> str | None:
    """(junior interview) Return the first line starting with "ERROR", or None.

    The input may be huge, so it must stop reading at the first hit rather than
    materialising everything.
    """
    raise NotImplementedError


def make_counter(start: int = 0) -> Callable[[], int]:
    """(junior interview) Return a function that increments and returns a private counter.

    >>> counter = make_counter()
    >>> counter(); counter()
    1
    2

    Two counters created separately must not share state.
    """
    raise NotImplementedError


def apply_all(value: float, *functions: Callable[[float], float]) -> float:
    """(basic) Apply the functions to ``value`` from left to right and return the result.

    >>> apply_all(2, lambda x: x + 1, lambda x: x * 10)
    30
    """
    raise NotImplementedError


def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    """(junior interview) Append ``tag`` to ``tags`` and return the list.

    When no list is given, start from an empty one. Calling this repeatedly without
    a list must NOT accumulate results across calls - that is the point of the task.
    """
    raise NotImplementedError


def summarise(
    values: list[float],
    *,
    precision: int = 2,
    include_extremes: bool = False,
) -> dict[str, float]:
    """(thinking) Return {"count", "total", "mean"} rounded to ``precision``.

    With ``include_extremes=True`` also add "min" and "max". An empty input gives
    count 0, total 0.0, mean 0.0 and no extremes.

    Note the keyword-only parameters: callers must name them.
    """
    raise NotImplementedError


def build_multipliers(factors: list[int]) -> list[Callable[[int], int]]:
    """(junior interview) Return one multiplier function per factor.

    >>> fns = build_multipliers([2, 3])
    >>> [fn(10) for fn in fns]
    [20, 30]

    The obvious one-liner is wrong - find out why (late binding) and fix it.
    """
    raise NotImplementedError
