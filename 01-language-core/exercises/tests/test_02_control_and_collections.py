import pytest

from tasks.task_02_control_and_collections import (
    chunk,
    first_matching,
    grade,
    group_by_first_letter,
    last_n_events,
    merge_configs,
    missing_fields,
    parse_command,
    top_n,
    unique_preserving_order,
    word_frequencies,
)


@pytest.mark.parametrize(
    "score,expected",
    [(100, "A"), (90, "A"), (89, "B"), (75, "B"), (74, "C"), (60, "C"), (59, "F"), (0, "F")],
)
def test_grade(score: int, expected: str) -> None:
    assert grade(score) == expected


@pytest.mark.parametrize("score", [-1, 101])
def test_grade_rejects_out_of_range(score: int) -> None:
    with pytest.raises(ValueError):
        grade(score)


def test_parse_command() -> None:
    assert parse_command("quit") == ("quit", [])
    assert parse_command("load report.csv") == ("load", ["report.csv"])
    assert parse_command("save out.csv --force") == ("save", ["out.csv", "--force"])


def test_parse_command_rejects_bad_input() -> None:
    with pytest.raises(ValueError):
        parse_command("")
    with pytest.raises(ValueError, match="delete"):
        parse_command("delete everything")


def test_first_matching() -> None:
    assert first_matching([1, 5, 9], 4) == 5
    with pytest.raises(LookupError):
        first_matching([1, 2], 10)


def test_unique_preserving_order() -> None:
    assert unique_preserving_order(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]
    assert unique_preserving_order([]) == []


def test_word_frequencies() -> None:
    assert word_frequencies("The cat, the CAT!") == {"the": 2, "cat": 2}
    assert word_frequencies("") == {}


def test_top_n_breaks_ties_alphabetically() -> None:
    assert top_n({"b": 2, "a": 2, "c": 1}, 2) == [("a", 2), ("b", 2)]
    assert top_n({"a": 1}, 5) == [("a", 1)]


def test_group_by_first_letter() -> None:
    assert group_by_first_letter(["anna", "bob", "alex"]) == {"A": ["anna", "alex"], "B": ["bob"]}


def test_missing_fields() -> None:
    record: dict[str, object] = {"name": "Anna", "email": None}
    assert missing_fields(["name", "email", "phone"], record) == {"email", "phone"}
    assert missing_fields([], record) == set()


def test_merge_configs_does_not_mutate() -> None:
    defaults: dict[str, object] = {"host": "localhost", "port": 5432}
    overrides: dict[str, object] = {"port": 5433}
    assert merge_configs(defaults, overrides) == {"host": "localhost", "port": 5433}
    assert defaults == {"host": "localhost", "port": 5432}


def test_chunk() -> None:
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunk([], 3) == []
    with pytest.raises(ValueError):
        chunk([1, 2], 0)


def test_last_n_events() -> None:
    assert last_n_events(["a", "b", "c", "d"], 2) == ["c", "d"]
    assert last_n_events(["a"], 5) == ["a"]
    assert last_n_events((str(i) for i in range(1000)), 3) == ["997", "998", "999"]
