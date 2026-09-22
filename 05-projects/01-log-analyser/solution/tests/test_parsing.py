from datetime import datetime, timedelta, timezone

import pytest

from loganalyse.parsing import normalise_path, parse_line, parse_timestamp

LINE = (
    '192.168.1.10 - - [27/Apr/2024:13:59:08 +0200] "GET /api/transactions?page=2 HTTP/1.1" '
    '200 4523 "https://app.example.com/" "Mozilla/5.0 (Windows NT 10.0)" 0.234'
)


def test_parses_a_complete_line() -> None:
    entry = parse_line(LINE)
    assert entry is not None
    assert entry.ip == "192.168.1.10"
    assert entry.timestamp == datetime(2024, 4, 27, 13, 59, 8, tzinfo=timezone(timedelta(hours=2)))
    assert entry.method == "GET"
    assert entry.path == "/api/transactions?page=2"
    assert entry.endpoint == "/api/transactions"
    assert entry.status == 200
    assert entry.size == 4523
    assert entry.referrer == "https://app.example.com/"
    assert entry.duration == 0.234


def test_duration_is_optional() -> None:
    entry = parse_line(LINE.rsplit(" ", 1)[0])
    assert entry is not None
    assert entry.duration is None


def test_missing_referrer_becomes_none() -> None:
    entry = parse_line(LINE.replace('"https://app.example.com/"', '"-"'))
    assert entry is not None
    assert entry.referrer is None


def test_dash_size_is_zero() -> None:
    entry = parse_line(LINE.replace(" 200 4523 ", " 304 - "))
    assert entry is not None
    assert entry.size == 0


@pytest.mark.parametrize(
    "line",
    [
        "",
        "   ",
        "this is not a log line",
        '192.168.1.10 - - [27/Apr/2024:13:59:08 +0200] "GET /api/x',
        '- - - [invalid timestamp] "GET / HTTP/1.1" 200 100 "-" "-"',
        '10.0.0.1 - - [27/Xyz/2024:13:59:08 +0200] "GET / HTTP/1.1" 200 100 "-" "-"',
    ],
)
def test_malformed_lines_return_none(line: str) -> None:
    assert parse_line(line) is None


def test_parse_timestamp_is_locale_independent() -> None:
    parsed = parse_timestamp("27/Apr/2024:13:59:08 +0200")
    assert parsed.year == 2024
    assert parsed.month == 4
    assert parsed.utcoffset() == timedelta(hours=2)


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/api/transactions?page=2", "/api/transactions"),
        ("/api/transactions/", "/api/transactions"),
        ("/api/users/1234/orders", "/api/users/{id}/orders"),
        ("/api/items/3fa85f64-5717-4562-b3fc-2c963f66afa6", "/api/items/{id}"),
        ("/", "/"),
        ("/static/app.js#top", "/static/app.js"),
    ],
)
def test_normalise_path(path: str, expected: str) -> None:
    assert normalise_path(path) == expected


def test_unusual_methods_are_accepted() -> None:
    entry = parse_line(LINE.replace('"GET ', '"PATCH '))
    assert entry is not None
    assert entry.method == "PATCH"
