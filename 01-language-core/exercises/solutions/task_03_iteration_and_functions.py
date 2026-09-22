"""Reference solution — chapters 05-06."""

from collections.abc import Callable, Iterable, Iterator
from functools import reduce


def active_emails(users: list[dict[str, object]]) -> list[str]:
    return [
        str(user["email"]).lower()
        for user in users
        if user.get("active") is True and "email" in user
    ]


def index_by(records: list[dict[str, object]], key: str) -> dict[object, dict[str, object]]:
    return {record[key]: record for record in records}


def running_total(values: Iterable[float]) -> Iterator[float]:
    # A generator: the body does not run until the caller asks for the first value,
    # and it keeps only the accumulator in memory.
    total = 0.0
    for value in values:
        total += value
        yield total


def read_valid_lines(lines: Iterable[str]) -> Iterator[tuple[int, str]]:
    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        yield line_no, line


def first_error(lines: Iterable[str]) -> str | None:
    # next() over a generator expression stops at the first match; the default
    # keeps it from raising StopIteration when there is none.
    return next((line for line in lines if line.startswith("ERROR")), None)


def make_counter(start: int = 0) -> Callable[[], int]:
    count = start

    def increment() -> int:
        nonlocal count  # without this, count += 1 would be a local variable
        count += 1
        return count

    return increment


def apply_all(value: float, *functions: Callable[[float], float]) -> float:
    return reduce(lambda acc, fn: fn(acc), functions, value)


def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    # `tags: list[str] = []` would create ONE list at definition time and share it
    # between every call. None as the sentinel is the standard fix.
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


def summarise(
    values: list[float],
    *,
    precision: int = 2,
    include_extremes: bool = False,
) -> dict[str, float]:
    if not values:
        return {"count": 0, "total": 0.0, "mean": 0.0}

    result = {
        "count": len(values),
        "total": round(sum(values), precision),
        "mean": round(sum(values) / len(values), precision),
    }
    if include_extremes:
        result["min"] = round(min(values), precision)
        result["max"] = round(max(values), precision)
    return result


def build_multipliers(factors: list[int]) -> list[Callable[[int], int]]:
    # [lambda x: x * factor for factor in factors] would capture the VARIABLE, so
    # every function would use the last factor. Binding it as a default argument
    # (or a factory function) captures the value at creation time.
    return [lambda x, factor=factor: x * factor for factor in factors]
