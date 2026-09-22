# Project 1 — Log analyser CLI

**Standard library only.** No pandas, no click, no third-party runtime dependency. The point is
to show that you can solve a real problem with the language itself.

## The story

Your team runs a web service behind nginx. When something goes wrong, someone downloads a few
hundred megabytes of access logs and asks the questions below. Today they do it with a pile of
`grep | awk | sort | uniq -c` one-liners that nobody can reproduce. You are building the tool
that replaces them.

## The input

Standard nginx *combined* log format, one request per line:

```
192.168.1.10 - - [27/Apr/2024:13:59:08 +0200] "GET /api/transactions?page=2 HTTP/1.1" 200 4523 "https://app.example.com/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" 0.234
```

| Field | Meaning |
|---|---|
| `192.168.1.10` | client IP |
| `[27/Apr/2024:13:59:08 +0200]` | timestamp with offset |
| `"GET /api/... HTTP/1.1"` | method, path, protocol |
| `200` | status code |
| `4523` | response size in bytes |
| `"https://..."` | referrer (`"-"` when absent) |
| `"Mozilla/5.0 ..."` | user agent |
| `0.234` | request duration in seconds (an nginx extension; may be missing) |

A generator for test data is provided: `generate_logs.py` (see below). Real logs contain
malformed lines — your parser must survive them.

## What it must do

```bash
# Summary of a file
loganalyse summary access.log

# Only a time window
loganalyse summary access.log --since "2024-04-27 00:00" --until "2024-04-28 00:00"

# Slowest endpoints
loganalyse slowest access.log --top 10

# Errors only, grouped
loganalyse errors access.log --status 5xx

# Machine-readable output for another tool
loganalyse summary access.log --format json

# Reading from a pipe
cat access.log | loganalyse summary -
```

### `summary`

```
File:            access.log
Lines:           124,338 (121 unparsable, 0.1%)
Period:          2024-04-27 00:00:04 - 2024-04-27 23:59:58
Requests:        124,217
Unique clients:  3,412
Total traffic:   1.4 GB

Status codes:
  2xx   118,004   95.0%
  3xx     2,110    1.7%
  4xx     3,401    2.7%
  5xx       702    0.6%

Top 5 paths:
  /api/transactions        41,203   33.2%
  /api/health              22,110   17.8%
  ...

Response time:  mean 0.142s  median 0.098s  p95 0.512s  p99 1.204s
```

### `slowest`

The top N paths by **mean** response time, with the request count and the p95, ignoring paths
seen fewer than 10 times (an endpoint called twice tells you nothing).

### `errors`

Every 4xx or 5xx grouped by `(status, path)`, most frequent first, with the first and last
occurrence timestamps.

## Requirements

### Functional

1. Parse the combined format, with the duration field optional.
2. Skip malformed lines — count them, and report them at `DEBUG` level with the line number.
3. Normalise paths: `/api/transactions?page=2` and `/api/transactions?page=3` are the same
   endpoint. Also collapse numeric path segments: `/users/1234/orders` → `/users/{id}/orders`.
4. `--since` / `--until` accept `YYYY-MM-DD` and `YYYY-MM-DD HH:MM`.
5. `--format json` prints valid JSON to stdout and nothing else.
6. `-` as the path reads from stdin.
7. Support gzipped input (`access.log.gz`) transparently.

### Non-functional

8. **Memory must not grow with file size.** A 2 GB log must work in a 200 MB process — so the
   file is streamed, and nothing accumulates per line. (Aggregates are fine; a list of every
   request is not.) Be ready to explain how you verified this.
9. Parsing is done once; the three commands share it.
10. `mypy --strict` clean, `ruff` clean.
11. Tests: unit tests for the parser (including malformed input, missing duration, unusual
    methods) and at least one end-to-end test invoking `main()` with a temporary file.

## Suggested structure

```
log-analyser/
├── pyproject.toml
├── README.md
├── src/loganalyse/
│   ├── __init__.py
│   ├── __main__.py        # argparse, dispatch, exit codes
│   ├── parsing.py         # line -> LogEntry | None
│   ├── stats.py           # LogEntry stream -> aggregates
│   ├── formatting.py      # aggregates -> text / JSON
│   └── models.py          # LogEntry, Summary dataclasses
└── tests/
    ├── test_parsing.py
    ├── test_stats.py
    └── test_cli.py
```

## Hints

- A regular expression per line, compiled once. Write it with named groups and
  `re.VERBOSE` so it stays readable.
- `datetime.strptime(raw, "%d/%b/%Y:%H:%M:%S %z")` parses the nginx timestamp. Note that `%b`
  is locale-dependent — think about what that means on a machine with a Hungarian locale.
- `collections.Counter` for the counts, `statistics.quantiles` for the percentiles.
- Percentiles need the durations. Keeping every duration in memory breaks requirement 8 for a
  huge file — decide between exact percentiles per path (bounded by the number of paths) and an
  approximation, and **write down** which you chose and why.
- `gzip.open(path, "rt", encoding="utf-8")` and `open(...)` return the same kind of object;
  one function can choose between them by extension.
- Generators all the way: `lines -> entries -> filtered entries -> aggregates`.

## Test data

`generate_logs.py` in this folder writes a realistic log file:

```bash
python generate_logs.py --lines 200000 --out access.log --malformed 0.001
```

## Acceptance criteria

- [ ] All three commands work on a generated 200k-line file
- [ ] `--format json` output parses with `json.loads`
- [ ] A file with 5% malformed lines produces a report, not a traceback
- [ ] An empty file produces a sensible message, not a `ZeroDivisionError`
- [ ] Memory stays flat as the file grows (demonstrate it)
- [ ] `pytest`, `mypy --strict`, `ruff check` all clean
- [ ] README explains the path-normalisation rules and the percentile decision

## Stretch

1. `--follow` (like `tail -f`): keep reading as the file grows.
2. Detect anomalies: a 5-minute window whose error rate is more than 3σ above the mean.
3. `--compare yesterday.log` — a side-by-side diff of the two summaries.
4. Benchmark it against `wc -l` and against the `grep | awk` pipeline it replaces, and put the
   numbers in the README.
