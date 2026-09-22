from decimal import Decimal

import pytest

from tasks.task_01_objects_and_types import (
    append_without_mutating,
    are_same_object,
    byte_length,
    deep_update,
    floor_and_remainder,
    format_report_line,
    initials,
    join_lines,
    normalise_name,
    safe_divide,
    total_with_vat,
)


def test_append_returns_new_list() -> None:
    original = [1, 2]
    result = append_without_mutating(original, 3)
    assert result == [1, 2, 3]
    assert original == [1, 2], "the original list must not be mutated"
    assert result is not original


def test_deep_update_leaves_inner_lists_alone() -> None:
    matrix = [[1, 2], [3, 4]]
    result = deep_update(matrix, 0, 1, 99)
    assert result == [[1, 99], [3, 4]]
    assert matrix == [[1, 2], [3, 4]]
    assert result[1] is not matrix[1], "a shallow copy is not enough here"


def test_are_same_object() -> None:
    a = [1, 2]
    b = a
    c = [1, 2]
    assert are_same_object(a, b) is True
    assert are_same_object(a, c) is False


def test_safe_divide() -> None:
    assert safe_divide(7, 2) == 3.5
    assert safe_divide(6, 3) == 2.0
    assert safe_divide(1, 0) is None


@pytest.mark.parametrize(
    "a,b,expected",
    [(7, 2, (3, 1)), (-7, 2, (-4, 1)), (7, -2, (-4, -1)), (8, 4, (2, 0))],
)
def test_floor_and_remainder(a: int, b: int, expected: tuple[int, int]) -> None:
    assert floor_and_remainder(a, b) == expected


def test_total_with_vat_is_exact() -> None:
    assert total_with_vat(["19.99", "0.02"], "0.00") == Decimal("20.01")
    assert total_with_vat(["0.10", "0.20"], "0.00") == Decimal("0.30")
    assert total_with_vat(["100.00"], "0.27") == Decimal("127.00")


def test_total_with_vat_returns_decimal() -> None:
    result = total_with_vat(["1.00"], "0.00")
    assert isinstance(result, Decimal), "float would lose precision"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  anna   MARIA  nagy ", "Anna Maria Nagy"),
        ("bob", "Bob"),
        ("\tBOB\n  smith ", "Bob Smith"),
    ],
)
def test_normalise_name(raw: str, expected: str) -> None:
    assert normalise_name(raw) == expected


def test_initials() -> None:
    assert initials("anna maria nagy") == "A.M.N."
    assert initials("Bob") == "B."


def test_format_report_line() -> None:
    expected = "Anna" + " " * 20 + "1,234.50" + " " * 4 + "8.7%"
    result = format_report_line("Anna", 1234.5, 0.0873)
    assert len(result) == 40
    assert result == expected


def test_join_lines() -> None:
    assert join_lines(["a", "b", "c"]) == "a\nb\nc"
    assert join_lines([]) == ""
    assert join_lines(["only"]) == "only"


def test_byte_length() -> None:
    assert byte_length("abc") == 3
    assert byte_length("Grüße") == 7
    assert byte_length("Grüße", "utf-16-le") == 10
