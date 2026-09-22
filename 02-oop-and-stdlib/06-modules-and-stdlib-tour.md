# 06 — The standard library you actually need

Python's standard library is large, and a junior who knows it reaches for a dependency far less
often. This chapter is a guided tour of the modules you will use in the first month on the job.

## `pathlib` — filesystem paths

Forget `os.path` string juggling. `Path` objects know how to combine, split and query paths, and
they work identically on Windows and Unix.

```python
from pathlib import Path

root = Path("data")
csv_path = root / "raw" / "transactions.csv"      # the / operator joins

csv_path.exists()
csv_path.is_file()
csv_path.suffix          # '.csv'
csv_path.stem            # 'transactions'
csv_path.name            # 'transactions.csv'
csv_path.parent          # Path('data/raw')
csv_path.resolve()       # absolute, symlinks resolved
csv_path.stat().st_size  # bytes

root.mkdir(parents=True, exist_ok=True)
list(root.glob("*.csv"))         # one level
list(root.rglob("*.csv"))        # recursive

text = csv_path.read_text(encoding="utf-8")       # small files, one call
csv_path.write_text(text, encoding="utf-8")
data = csv_path.read_bytes()

Path("old.csv").rename("new.csv")
Path("tmp.csv").unlink(missing_ok=True)
```

Use `Path` in your signatures (`def load(path: Path) -> ...`), accept `str | Path` at the edges
of your library, and convert once with `Path(path)`.

## `datetime` — dates and times

```python
from datetime import datetime, date, time, timedelta, timezone, UTC

date.today()                        # date(2026, 9, 17)
datetime.now()                      # naive local time - avoid
datetime.now(UTC)                   # aware, in UTC - prefer this

d = date(2024, 5, 1)
dt = datetime(2024, 5, 1, 14, 30, tzinfo=UTC)

# Parsing and formatting
datetime.strptime("2024-05-01 14:30", "%Y-%m-%d %H:%M")
datetime.fromisoformat("2024-05-01T14:30:00+00:00")     # the fast path for ISO input
dt.strftime("%Y-%m-%d")             # '2024-05-01'
dt.isoformat()                      # '2024-05-01T14:30:00+00:00'

# Arithmetic
dt + timedelta(days=7, hours=3)
(date(2024, 12, 24) - date.today()).days
```

Two rules that save whole days of debugging:

1. **Store and compute in UTC**, convert to local time only for display. A `datetime` without
   `tzinfo` ("naive") is a bug waiting for a daylight-saving transition.
2. `datetime` is a subclass of `date`, so `isinstance(dt, date)` is `True` — a classic trap when
   branching on type.

Time zones come from the standard library since 3.9:

```python
from zoneinfo import ZoneInfo

budapest = ZoneInfo("Europe/Budapest")
local = datetime.now(UTC).astimezone(budapest)
```

## `re` — regular expressions

```python
import re

pattern = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")     # compile once, reuse

match = pattern.match("2024-05-01")
if match:
    year, month, day = match.groups()
    print(match.group(1))

re.search(r"ERROR (\w+)", line)        # anywhere in the string
re.findall(r"\d+", text)               # every match, as a list
re.sub(r"\s+", " ", text)              # replace
re.split(r"[;,]", text)                # split on either character

# Named groups make the code readable
m = re.match(r"(?P<level>\w+):(?P<message>.*)", line)
m["level"], m["message"]
```

`match` anchors at the start, `search` does not, `fullmatch` requires the whole string. Always
use raw strings (`r"..."`) for patterns.

**Do not parse structured formats with regexes.** CSV, JSON, HTML and URLs all have proper
parsers in the standard library; a regex will be wrong in edge cases you have not imagined.

## `logging` — instead of `print`

```python
import logging

logger = logging.getLogger(__name__)      # one logger per module, named by module


def process(path: Path) -> None:
    logger.info("processing %s", path)              # lazy formatting, note the comma
    try:
        ...
    except OSError:
        logger.exception("failed to read %s", path)  # includes the traceback
```

Configuration happens **once**, in the application entry point — never in a library module:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

Levels: `DEBUG` (detail for developers) < `INFO` (normal progress) < `WARNING` (something is
off) < `ERROR` (an operation failed) < `CRITICAL` (the process cannot continue).

The `%s` style matters: `logger.debug("value: %s", expensive())` still evaluates `expensive()`,
but the *formatting* is skipped when the level is off. With an f-string you also pay for the
formatting of every suppressed record.

## `collections` — beyond the built-ins

```python
from collections import Counter, defaultdict, deque, namedtuple, ChainMap

Counter(words).most_common(5)
defaultdict(list)
deque(maxlen=1000)
ChainMap(cli_args, env_vars, defaults)      # layered lookup, first hit wins
```

## `itertools` and `functools`

Covered in [01-language-core/05](../01-language-core/05-iteration-and-comprehensions.md) and
[01-language-core/06](../01-language-core/06-functions.md). The ones worth remembering:
`chain`, `islice`, `groupby`, `product`, `combinations`, `pairwise`; `cache`, `lru_cache`,
`partial`, `reduce`, `wraps`.

## `os` and `sys` — the process and its environment

```python
import os, sys

os.environ.get("DATABASE_URL", "sqlite:///local.db")
os.cpu_count()

sys.argv            # command-line arguments
sys.exit(1)         # exit code
sys.executable      # the current interpreter
sys.platform        # 'win32', 'linux', 'darwin'
sys.stderr.write("...")
```

Read configuration from `os.environ`, never hard-code secrets. `python-dotenv` loads a local
`.env` file into `os.environ` for development.

## `json`, `csv`, `sqlite3`, `argparse`, `subprocess`

Each gets proper treatment later:

- `json`, `csv` → [08-files-and-serialization.md](08-files-and-serialization.md)
- `argparse` → [04-building-applications/01-cli-and-configuration.md](../04-building-applications/01-cli-and-configuration.md)
- `sqlite3` → [04-building-applications/03-databases.md](../04-building-applications/03-databases.md)

```python
import subprocess

result = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    capture_output=True, text=True, check=True,      # check=True raises on failure
)
print(result.stdout.strip())
```

Pass a **list** of arguments, not a string, and never `shell=True` with user input — that is a
shell injection.

## Numbers, randomness, statistics

```python
import math, random, statistics
from decimal import Decimal
from fractions import Fraction

math.isclose(a, b), math.floor(x), math.ceil(x), math.sqrt(x), math.inf, math.nan
random.random(), random.randint(1, 6), random.choice(items), random.sample(items, 3)
random.shuffle(items)                       # in place
statistics.mean(xs), statistics.median(xs), statistics.stdev(xs)
```

`random` is **not** cryptographically secure. For tokens and passwords use `secrets`:

```python
import secrets
secrets.token_urlsafe(32)
```

## Other modules worth knowing exist

| Module | For |
|---|---|
| `dataclasses` | structured data (chapter 03) |
| `enum` | enumerations (chapter 03) |
| `typing` | annotations (chapter 05) |
| `unittest.mock` | mocking (chapter 09) |
| `tempfile` | temporary files and directories, cleaned up for you |
| `shutil` | copy, move, delete trees, disk usage |
| `zipfile`, `tarfile`, `gzip` | archives |
| `hashlib` | SHA-256 and friends |
| `uuid` | identifiers |
| `textwrap` | wrapping and dedenting text |
| `pprint` | readable printing of nested structures |
| `timeit` | micro-benchmarks |
| `configparser`, `tomllib` | INI and TOML config files (`tomllib` is read-only, 3.11+) |
| `urllib.parse` | building and parsing URLs correctly |
| `concurrent.futures` | thread and process pools (module 04) |
| `asyncio` | async I/O (module 04) |

## How to find things

```python
help(str.split)          # in the REPL
dir(obj)                 # what attributes does this object have
import inspect
inspect.signature(func)
inspect.getsource(func)  # the source, when available
```

And the documentation: [docs.python.org/3/library](https://docs.python.org/3/library/) — the
module index is worth skimming once, so you know what exists. That habit alone separates a
junior who adds a dependency for `str.removeprefix` from one who does not.

## Check yourself

1. Why `pathlib` instead of string concatenation?
2. What is a naive vs an aware `datetime`, and which should you store?
3. Why is `logger.info("x: %s", value)` preferable to an f-string?
4. Where should logging be configured, and where should it not?
5. Why must you pass a list to `subprocess.run`, and why avoid `shell=True`?
6. When is `random` the wrong module, and what replaces it?
