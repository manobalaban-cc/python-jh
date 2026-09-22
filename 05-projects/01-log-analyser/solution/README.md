# Log analyser — reference solution

```bash
python -m venv .venv && .venv/Scripts/activate
python -m pip install -e ".[dev]"

python ../generate_logs.py --lines 200000 --out access.log --malformed 0.001

loganalyse summary access.log
loganalyse summary access.log --since "2024-04-27 08:00" --until "2024-04-27 18:00"
loganalyse slowest access.log --top 10
loganalyse errors access.log --status 5xx
loganalyse summary access.log --format json | jq .
cat access.log | loganalyse summary -

pytest
mypy src/
ruff check .
```

## Structure

```
src/loganalyse/
├── models.py      LogEntry, PathStats - data only
├── parsing.py     line -> LogEntry | None, path normalisation, file opening
├── stats.py       stream of lines -> Summary, and the derived reports
├── formatting.py  Summary -> text / JSON
└── __main__.py    argparse, dispatch, exit codes
```

The dependency direction is one-way: `__main__` → `formatting`/`stats` → `parsing` → `models`.
Nothing below `__main__` knows about the command line, and nothing except `parsing` and
`__main__` touches a file. That is what makes `aggregate()` testable with a list of strings.

## Design decisions worth defending in review

### 1. Generators end to end

`open_log()` returns a file object, which is an iterator over lines; `aggregate()` consumes it
lazily. At no point does the whole file exist in memory. This is requirement 8, and it is the
reason the pipeline is built from generators rather than lists.

Verified with:

```bash
python -m generate_logs --lines 5000000 --out big.log      # ~800 MB
/usr/bin/time -v loganalyse summary big.log                 # Linux
python -c "import tracemalloc, ..."                         # or tracemalloc in-process
```

Peak memory stays flat as the file grows — except for the two deliberate exceptions below.

### 2. What we *do* keep in memory

Three things grow, and all three are bounded by cardinality rather than by request count:

| Kept | Bounded by | Why it is acceptable |
|---|---|---|
| `clients` (a set of IPs) | distinct client addresses | needed for "unique clients"; a real log has thousands, not millions |
| `endpoints` (a dict) | distinct endpoints **after normalisation** | this is exactly why we normalise paths: without it, `/users/1234` would create a new key per user |
| `durations` (a list) | number of requests **with a duration** | the one real compromise — see below |

### 3. Exact percentiles, and the trade-off

Percentiles need the distribution. Keeping every duration costs about 8 bytes per request —
~80 MB for 10 million requests, which is acceptable for a CLI tool run on demand, and it gives
**exact** answers.

The alternatives, considered and rejected for this scope:

- **t-digest / HDR histogram**: constant memory, approximate percentiles. The right answer for a
  long-running service; unnecessary complexity here.
- **Fixed-width histogram buckets**: simple and constant, but the accuracy depends on the bucket
  layout, which depends on the traffic you have not seen yet.

If the requirement ever becomes "must handle a 100 GB log", the change is confined to
`Summary.durations` and `duration_stats()` — which is the point of keeping the aggregation in
one module.

### 4. Parsing the timestamp without `strptime("%b")`

`%b` is locale-dependent: on a machine with a Hungarian locale, `strptime("Apr", "%b")` fails,
and every single line becomes unparsable. A three-line month lookup removes an entire class of
"works on my machine" bug. This is the kind of detail the exercise is really about.

### 5. Malformed lines never abort the run

`parse_line` returns `None` rather than raising: an unparsable line is expected input for this
tool, not an exceptional condition. The count is reported, and the lines themselves go to
`DEBUG` logging so `-vv` shows them without flooding normal output.

### 6. `main(argv=None) -> int`

The CLI is a thin shell: parse arguments, open the file, aggregate, format, print. Because
`main` takes `argv` and returns an exit code, the end-to-end tests call it directly with a list
and assert on captured stdout — no subprocess, no server, milliseconds per test.

## What is deliberately not handled

- **`--follow`** (tail -f) — listed as a stretch goal.
- **Multiple files / globs** — `cat *.log | loganalyse summary -` covers it.
- **Timezone-aware `--since`/`--until`** — the filters are interpreted in the log's own offset.
  Documented, not silently wrong.
- **Bot filtering** — the user agent is parsed and kept, but nothing uses it yet.

## Test coverage

32 tests: the parser (valid, malformed, optional fields, unusual methods, path normalisation,
locale independence), the aggregation (counting, grouping, time windows, empty input), and the
CLI end to end (text, JSON, gzip, missing file, bad arguments, exit codes).
