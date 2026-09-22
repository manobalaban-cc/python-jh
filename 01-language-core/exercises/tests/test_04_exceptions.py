from decimal import Decimal
from pathlib import Path

import pytest

from tasks.task_04_exceptions import (
    ImportFailure,
    SourceUnavailable,
    ValidationError,
    dig,
    load_settings,
    parse_amount,
    process_records,
    retry,
)


def test_exception_hierarchy() -> None:
    assert issubclass(ValidationError, ImportFailure)
    assert issubclass(SourceUnavailable, ImportFailure)
    assert issubclass(ImportFailure, Exception)


def test_validation_error_carries_structured_data() -> None:
    error = ValidationError("amount", "not a number")
    assert error.field == "amount"
    assert error.reason == "not a number"
    assert str(error) == "amount: not a number"


def test_parse_amount_accepts_valid_input() -> None:
    assert parse_amount("19.99") == Decimal("19.99")
    assert parse_amount("  42 ") == Decimal("42")


@pytest.mark.parametrize("text", ["abc", "", "-1"])
def test_parse_amount_rejects_bad_input(text: str) -> None:
    with pytest.raises(ValidationError):
        parse_amount(text)


def test_parse_amount_keeps_the_cause() -> None:
    with pytest.raises(ValidationError) as info:
        parse_amount("abc")
    assert info.value.__cause__ is not None, "use `raise ... from exc`"


def test_dig() -> None:
    data: dict[str, object] = {"a": {"b": {"c": 1}}}
    assert dig(data, "a", "b", "c") == 1
    assert dig(data, "a", "b") == {"c": 1}
    assert dig(data, "a", "x", "c") is None
    assert dig({"a": 5}, "a", "b") is None, "must survive a non-dict value"
    assert dig(data) == data


def test_retry_succeeds_eventually() -> None:
    calls = 0

    def flaky() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ConnectionError("boom")
        return "ok"

    assert retry(flaky) == "ok"
    assert calls == 3


def test_retry_gives_up_and_chains() -> None:
    def always_fails() -> str:
        raise TimeoutError("nope")

    with pytest.raises(SourceUnavailable) as info:
        retry(always_fails, attempts=2)
    assert "2" in str(info.value)
    assert isinstance(info.value.__cause__, TimeoutError)


def test_retry_does_not_swallow_programming_errors() -> None:
    def broken() -> str:
        raise ValueError("this is a bug, not a transport failure")

    with pytest.raises(ValueError):
        retry(broken)


def test_process_records_collects_errors() -> None:
    records = [
        {"amount": "10.00"},
        {"amount": "oops"},
        {"name": "no amount here"},
        {"amount": "5"},
    ]
    amounts, errors = process_records(records)

    assert amounts == [Decimal("10.00"), Decimal("5")]
    assert len(errors) == 2
    assert errors[0].startswith("row 2:")
    assert errors[1].startswith("row 3:")


def test_load_settings_missing_file_returns_defaults() -> None:
    defaults = {"host": "localhost"}
    assert load_settings("does-not-exist.cfg", defaults) == {"host": "localhost"}
    assert defaults == {"host": "localhost"}


def test_load_settings_overrides(tmp_path: Path) -> None:
    config = tmp_path / "app.cfg"
    config.write_text("# comment\n\nport = 5433\nhost=db.internal\n", encoding="utf-8")

    result = load_settings(str(config), {"host": "localhost", "port": "5432", "debug": "0"})
    assert result == {"host": "db.internal", "port": "5433", "debug": "0"}
