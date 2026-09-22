import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from txlib.errors import SourceError, TxError, ValidationError
from txlib.instrumentation import Timer, timed
from txlib.loading import load_file
from txlib.models import Currency, Money
from txlib.parsing import parse_row
from txlib.repository import InMemoryRepository

GOOD_ROW = {
    "Timestamp": "2024-04-27 13:59:08",
    "Amount": "815.85",
    "Currency": "GBP",
    "Recipient": " Amazon ",
}


def test_exception_hierarchy() -> None:
    assert issubclass(ValidationError, TxError)
    assert issubclass(SourceError, TxError)


def test_parse_row_builds_a_transaction() -> None:
    transaction = parse_row(GOOD_ROW, 1)
    assert transaction.timestamp == datetime(2024, 4, 27, 13, 59, 8)
    assert transaction.money == Money(Decimal("815.85"), Currency.GBP)
    assert transaction.recipient == "Amazon", "the recipient must be stripped"


@pytest.mark.parametrize("field", ["Timestamp", "Amount", "Currency", "Recipient"])
def test_parse_row_rejects_missing_fields(field: str) -> None:
    row = GOOD_ROW | {field: ""}
    with pytest.raises(ValidationError) as info:
        parse_row(row, 7)
    assert info.value.field == field
    assert info.value.row_number == 7


def test_parse_row_rejects_bad_timestamp() -> None:
    with pytest.raises(ValidationError) as info:
        parse_row(GOOD_ROW | {"Timestamp": "27/04/2024"}, 1)
    assert info.value.field == "Timestamp"
    assert info.value.__cause__ is not None, "keep the original error as the cause"


def test_parse_row_rejects_bad_amount() -> None:
    with pytest.raises(ValidationError) as info:
        parse_row(GOOD_ROW | {"Amount": "eight hundred"}, 1)
    assert info.value.field == "Amount"


def test_parse_row_rejects_negative_amount() -> None:
    with pytest.raises(ValidationError):
        parse_row(GOOD_ROW | {"Amount": "-5"}, 1)


def test_parse_row_rejects_unknown_currency() -> None:
    with pytest.raises(ValidationError) as info:
        parse_row(GOOD_ROW | {"Currency": "XXX"}, 1)
    assert info.value.field == "Currency"
    assert "EUR" in str(info.value), "list the accepted values in the message"


def test_load_file_imports_every_valid_row(valid_csv: Path) -> None:
    repository = InMemoryRepository()
    result = load_file(valid_csv, repository)

    assert result.imported == 3
    assert result.skipped == 0
    assert result.errors == []
    assert len(repository.all()) == 3


def test_load_file_keeps_going_after_bad_rows(messy_csv: Path) -> None:
    repository = InMemoryRepository()
    result = load_file(messy_csv, repository)

    assert result.imported == 2
    assert result.skipped == 3
    assert result.total == 5
    assert {error.field for error in result.errors} == {"Timestamp", "Amount", "Currency"}


def test_load_file_reports_row_numbers(messy_csv: Path) -> None:
    result = load_file(messy_csv, InMemoryRepository())
    assert [error.row_number for error in result.errors] == [2, 3, 4]


def test_load_file_raises_source_error_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(SourceError) as info:
        load_file(tmp_path / "nope.csv", InMemoryRepository())
    assert isinstance(info.value.__cause__, FileNotFoundError)


def test_load_file_raises_source_error_for_wrong_columns(tmp_path: Path) -> None:
    path = tmp_path / "other.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(SourceError, match="missing columns"):
        load_file(path, InMemoryRepository())


def test_totals_by_recipient(valid_csv: Path) -> None:
    repository = InMemoryRepository()
    load_file(valid_csv, repository)

    totals = repository.totals_by_recipient()
    assert totals[("Amazon", Currency.GBP)] == Money(Decimal("935.85"), Currency.GBP)
    assert totals[("Starbucks", Currency.JPY)] == Money(Decimal("373.09"), Currency.JPY)


def test_repository_all_returns_a_copy(valid_csv: Path) -> None:
    repository = InMemoryRepository()
    load_file(valid_csv, repository)

    rows = repository.all()
    rows.clear()
    assert len(repository.all()) == 3, "callers must not be able to mutate internal state"


def test_timed_preserves_metadata() -> None:
    @timed
    def example(value: int) -> int:
        """Docstring survives."""
        return value * 2

    assert example(21) == 42
    assert example.__name__ == "example", "use functools.wraps"
    assert example.__doc__ == "Docstring survives."


def test_timed_logs(caplog: pytest.LogCaptureFixture) -> None:
    @timed
    def example() -> None: ...

    with caplog.at_level(logging.INFO):
        example()
    assert "example took" in caplog.text


def test_timer_context_manager_measures_and_does_not_swallow() -> None:
    with Timer("block") as timer:
        pass
    assert timer.elapsed >= 0

    with pytest.raises(ValueError), Timer("failing"):
        raise ValueError("boom")
