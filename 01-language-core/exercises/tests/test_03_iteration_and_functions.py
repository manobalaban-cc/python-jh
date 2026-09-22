from collections.abc import Iterator
from itertools import count, islice

import pytest

from tasks.task_03_iteration_and_functions import (
    active_emails,
    add_tag,
    apply_all,
    build_multipliers,
    first_error,
    index_by,
    make_counter,
    read_valid_lines,
    running_total,
    summarise,
)

USERS: list[dict[str, object]] = [
    {"name": "Anna", "email": "Anna@Example.COM", "active": True},
    {"name": "Bob", "email": "bob@example.com", "active": False},
    {"name": "Cecil", "active": True},
    {"name": "Dave", "email": "dave@example.com", "active": True},
]


def test_active_emails() -> None:
    assert active_emails(USERS) == ["anna@example.com", "dave@example.com"]
    assert active_emails([]) == []


def test_index_by() -> None:
    records: list[dict[str, object]] = [
        {"id": 1, "v": "a"},
        {"id": 2, "v": "b"},
        {"id": 1, "v": "c"},
    ]
    result = index_by(records, "id")
    assert set(result) == {1, 2}
    assert result[1]["v"] == "c", "the later record must win"


def test_running_total_values() -> None:
    assert list(running_total([1, 2, 3])) == [1, 3, 6]
    assert list(running_total([])) == []


def test_running_total_is_lazy() -> None:
    result = running_total(count(1))  # an infinite source
    assert isinstance(result, Iterator)
    assert list(islice(result, 4)) == [1, 3, 6, 10]


def test_read_valid_lines() -> None:
    lines = ["first", "", "  # comment", "  second  ", "#x"]
    assert list(read_valid_lines(lines)) == [(1, "first"), (4, "second")]


def test_first_error() -> None:
    assert first_error(["INFO ok", "ERROR boom", "ERROR again"]) == "ERROR boom"
    assert first_error(["INFO ok"]) is None


def test_first_error_stops_early() -> None:
    consumed = 0

    def source() -> Iterator[str]:
        nonlocal consumed
        for line in ["INFO a", "ERROR b", "INFO c", "INFO d"]:
            consumed += 1
            yield line

    assert first_error(source()) == "ERROR b"
    assert consumed == 2, "it must stop at the first match, not read everything"


def test_make_counter_is_independent() -> None:
    a = make_counter()
    b = make_counter(10)
    assert [a(), a(), a()] == [1, 2, 3]
    assert b() == 11
    assert a() == 4, "the two counters must not share state"


def test_apply_all() -> None:
    assert apply_all(2, lambda x: x + 1, lambda x: x * 10) == 30
    assert apply_all(5) == 5


def test_add_tag_has_no_shared_default() -> None:
    assert add_tag("a") == ["a"]
    assert add_tag("b") == ["b"], "the default list must not persist between calls"
    existing = ["x"]
    assert add_tag("y", existing) == ["x", "y"]


def test_summarise() -> None:
    assert summarise([1.0, 2.0, 4.0]) == {"count": 3, "total": 7.0, "mean": 2.33}
    assert summarise([1.0, 2.0, 4.0], precision=1) == {"count": 3, "total": 7.0, "mean": 2.3}
    assert summarise([]) == {"count": 0, "total": 0.0, "mean": 0.0}


def test_summarise_extremes() -> None:
    result = summarise([1.0, 5.0], include_extremes=True)
    assert result["min"] == 1.0
    assert result["max"] == 5.0


def test_summarise_options_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        summarise([1.0], 1)  # type: ignore[misc]


def test_build_multipliers_binds_each_factor() -> None:
    functions = build_multipliers([2, 3, 10])
    assert [fn(10) for fn in functions] == [20, 30, 100]
