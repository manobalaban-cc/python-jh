"""Reference solution — chapters 03-04."""

from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Sequence


def grade(score: int) -> str:
    if not 0 <= score <= 100:  # chained comparison
        raise ValueError(f"score out of range: {score}")
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    return "F"


def parse_command(command: str) -> tuple[str, list[str]]:
    match command.split():
        case []:
            raise ValueError("empty command")
        case ["quit"]:
            return "quit", []
        case ["load", *args] | ["save", *args] if args:
            action, *rest = command.split()
            return action, rest
        case [action, *_]:
            raise ValueError(f"unknown or incomplete command: {action}")
        case _:  # pragma: no cover - unreachable
            raise ValueError(command)


def first_matching(items: Sequence[int], threshold: int) -> int:
    for item in items:
        if item > threshold:
            return item
    else:
        # Reached only when the loop completed without break/return.
        raise LookupError("no element above threshold")


def unique_preserving_order(items: Iterable[str]) -> list[str]:
    # dict keys are unique AND ordered since 3.7, which makes this a one-liner.
    return list(dict.fromkeys(items))


def word_frequencies(text: str) -> dict[str, int]:
    words = (word.strip(".,!?;:").lower() for word in text.split())
    return dict(Counter(word for word in words if word))


def top_n(counts: dict[str, int], n: int) -> list[tuple[str, int]]:
    # Sort by count descending, then by key ascending. Returning -count in the key
    # tuple is the standard trick for mixing directions in a single sort.
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ordered[:n]


def group_by_first_letter(names: Iterable[str]) -> dict[str, list[str]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for name in names:
        groups[name[0].upper()].append(name)
    return dict(groups)


def missing_fields(required: Iterable[str], record: dict[str, object]) -> set[str]:
    return {field for field in required if record.get(field) is None}


def merge_configs(defaults: dict[str, object], overrides: dict[str, object]) -> dict[str, object]:
    # The | operator (3.9+) builds a new dict; defaults.update(overrides) would
    # mutate the argument, which the task forbids.
    return defaults | overrides


def chunk(items: Sequence[int], size: int) -> list[list[int]]:
    if size <= 0:
        raise ValueError(f"size must be positive, got {size}")
    return [list(items[i : i + size]) for i in range(0, len(items), size)]


def last_n_events(events: Iterable[str], n: int) -> list[str]:
    # A bounded deque drops the oldest element automatically, so memory stays O(n)
    # no matter how long the stream is.
    window: deque[str] = deque(maxlen=n)
    window.extend(events)
    return list(window)
