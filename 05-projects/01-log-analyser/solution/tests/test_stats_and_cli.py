import json
from datetime import datetime
from pathlib import Path

import pytest

from loganalyse.__main__ import main
from loganalyse.stats import aggregate, error_reports, percentile, slowest_endpoints

LINES = [
    '10.0.0.1 - - [27/Apr/2024:10:00:00 +0200] "GET /api/a HTTP/1.1" 200 100 "-" "ua" 0.1',
    '10.0.0.2 - - [27/Apr/2024:10:00:01 +0200] "GET /api/a?x=1 HTTP/1.1" 200 200 "-" "ua" 0.3',
    '10.0.0.1 - - [27/Apr/2024:11:00:00 +0200] "GET /api/b/42 HTTP/1.1" 500 0 "-" "ua" 2.0',
    '10.0.0.3 - - [28/Apr/2024:09:00:00 +0200] "GET /api/a HTTP/1.1" 404 50 "-" "ua" 0.2',
    "garbage line",
]


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    path = tmp_path / "access.log"
    path.write_text("\n".join(LINES) + "\n", encoding="utf-8")
    return path


def test_aggregate_counts() -> None:
    summary = aggregate(LINES)
    assert summary.total_lines == 5
    assert summary.unparsable == 1
    assert summary.requests == 4
    assert len(summary.clients) == 3
    assert summary.bytes_sent == 350


def test_aggregate_groups_normalised_endpoints() -> None:
    summary = aggregate(LINES)
    assert summary.endpoints["/api/a"].requests == 3, "?x=1 must not create a second endpoint"
    assert summary.endpoints["/api/b/{id}"].requests == 1


def test_aggregate_status_classes() -> None:
    summary = aggregate(LINES)
    assert summary.status_classes == {"2xx": 2, "5xx": 1, "4xx": 1}


def test_time_window_filter() -> None:
    summary = aggregate(LINES, since=datetime(2024, 4, 28))
    assert summary.requests == 1
    assert summary.total_lines == 5, "filtering must not change the line count"


def test_errors_are_grouped_with_first_and_last_seen() -> None:
    reports = error_reports(aggregate(LINES))
    assert {(r.status, r.endpoint) for r in reports} == {(500, "/api/b/{id}"), (404, "/api/a")}

    server_errors = error_reports(aggregate(LINES), status_class="5xx")
    assert len(server_errors) == 1
    assert server_errors[0].status == 500


def test_slowest_endpoints_respects_min_requests() -> None:
    summary = aggregate(LINES)
    assert slowest_endpoints(summary, min_requests=10) == []

    reports = slowest_endpoints(summary, min_requests=1)
    assert reports[0].endpoint == "/api/b/{id}"
    assert reports[0].mean_duration == pytest.approx(2.0)


def test_percentile() -> None:
    values = [float(i) for i in range(1, 101)]
    assert percentile(values, 0.95) == 96.0
    assert percentile([], 0.95) == 0.0


def test_empty_input_does_not_divide_by_zero() -> None:
    summary = aggregate([])
    assert summary.requests == 0
    assert summary.unparsable_share == 0.0


# --- CLI ---------------------------------------------------------------------


def test_cli_summary(log_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["summary", str(log_file)]) == 0
    out = capsys.readouterr().out
    assert "Requests:        4" in out
    assert "/api/a" in out


def test_cli_json_output_is_valid(log_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["summary", str(log_file), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["requests"] == 4
    assert payload["unparsable"] == 1


def test_cli_missing_file_returns_1(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["summary", "no-such-file.log"]) == 1


def test_cli_rejects_bad_date(log_file: Path) -> None:
    with pytest.raises(SystemExit) as info:
        main(["summary", str(log_file), "--since", "yesterday"])
    assert info.value.code == 2


def test_cli_errors_command(log_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["errors", str(log_file), "--status", "5xx"]) == 0
    assert "/api/b/{id}" in capsys.readouterr().out


def test_cli_handles_gzip(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    import gzip

    path = tmp_path / "access.log.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("\n".join(LINES) + "\n")

    assert main(["summary", str(path)]) == 0
    assert "Requests:        4" in capsys.readouterr().out
