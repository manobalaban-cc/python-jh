# 08 — Files, encodings, CSV, JSON

## Reading and writing text

```python
from pathlib import Path

# Small file, one shot
text = Path("report.txt").read_text(encoding="utf-8")
Path("report.txt").write_text(text, encoding="utf-8")

# Large file, line by line - constant memory
with open("huge.log", encoding="utf-8") as f:
    for line in f:                       # the file object is an iterator over lines
        process(line.rstrip("\n"))

# Writing
with open("out.txt", "w", encoding="utf-8", newline="") as f:
    f.write("first\n")
    f.writelines(lines)
```

Modes: `r` read, `w` write (**truncates!**), `a` append, `x` create-or-fail, `b` binary,
`+` read and write. `"w"` on an existing file destroys it without asking — `"x"` is the safe
choice when you mean "create new".

### Always specify the encoding

```python
open("data.csv")                          # platform-dependent default - a bug on Windows
open("data.csv", encoding="utf-8")        # correct
```

On Windows the default is still the legacy code page, so a file written on a colleague's Linux
machine comes back with mangled accented characters. Pass `encoding="utf-8"` every time.

Files with a byte-order mark (Excel likes emitting them) need `encoding="utf-8-sig"`, which
strips it. For files you cannot control:

```python
text = path.read_text(encoding="utf-8", errors="replace")     # never crashes, may mangle
```

### `newline=""` when writing CSV

Without it, the `csv` module's `\r\n` plus Windows' translation produces blank lines between
rows. This is the single most common "why does my CSV have empty rows" question.

## CSV

```python
import csv
from pathlib import Path

# Reading as dicts - preferred, the columns are named
with open("data/transactions.csv", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["Amount"], row["Currency"])      # every value is a str!

# Reading as lists
with open(path, encoding="utf-8", newline="") as f:
    reader = csv.reader(f, delimiter=";")
    header = next(reader)
    for row in reader:
        ...

# Writing
rows = [{"name": "Anna", "amount": 100}, {"name": "Bob", "amount": 250}]
with open("out.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "amount"])
    writer.writeheader()
    writer.writerows(rows)
```

Three things the `csv` module handles that a `line.split(",")` does not: quoted fields
containing the delimiter, embedded newlines, and escaped quotes. Never split CSV by hand.

Dialects differ — a "CSV" exported by a Hungarian or German Excel is usually semicolon-separated
with a comma as the decimal mark:

```python
csv.reader(f, delimiter=";")
float(value.replace(",", "."))
```

For anything analytical, `pandas.read_csv` (module 03) is far more convenient. Use the `csv`
module when you are streaming, when the file is huge, or when you want no dependencies.

## JSON

```python
import json
from pathlib import Path

# String <-> object
data = json.loads('{"name": "Anna", "age": 32}')       # str  -> dict
text = json.dumps(data, ensure_ascii=False, indent=2)  # dict -> str

# File <-> object  (note: load/dump, no "s")
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

with open("out.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

`ensure_ascii=False` keeps non-ASCII characters readable instead of escaping them to `á`.

The type mapping:

| JSON | Python |
|---|---|
| object | `dict` |
| array | `list` |
| string | `str` |
| number | `int` / `float` |
| true / false | `True` / `False` |
| null | `None` |

Everything else needs help. `datetime`, `Decimal`, `set` and your own classes are **not**
serialisable by default:

```python
from datetime import date, datetime
from decimal import Decimal


def default(obj: object) -> str:
    if isinstance(obj, datetime | date):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)              # str, not float - preserves precision
    raise TypeError(f"not serialisable: {type(obj).__name__}")


json.dumps(data, default=default)
```

For dataclasses, `dataclasses.asdict()` first, then `json.dumps`. When the structure is a real
API contract, use Pydantic (module 04) — it handles serialisation and validation together.

**Security note:** `json` is safe to use on untrusted input. `pickle` is **not** — unpickling
executes arbitrary code. Never load a pickle you did not create.

## Temporary files

```python
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "work.csv"
    path.write_text("...", encoding="utf-8")
# the directory and everything in it is gone here
```

This is also how you write tests that touch the filesystem — though `pytest`'s `tmp_path`
fixture (chapter 09) does it for you.

## Binary files and hashing

```python
data = Path("image.png").read_bytes()

import hashlib
digest = hashlib.sha256(data).hexdigest()

# Large file, streaming
h = hashlib.sha256()
with open("big.iso", "rb") as f:
    while chunk := f.read(1024 * 1024):
        h.update(chunk)
```

## Other formats you will meet

| Format | Tool | Note |
|---|---|---|
| Excel `.xlsx` | `pandas.read_excel` + `openpyxl` | module 03; the datasets in `data/` include some |
| Parquet | `pandas.read_parquet` + `pyarrow` | columnar, compressed, keeps dtypes — prefer it over CSV for intermediate data |
| TOML | `tomllib` (read-only, 3.11+) | configuration, e.g. `pyproject.toml` |
| YAML | `PyYAML` (external) | use `yaml.safe_load`, never `yaml.load` |
| XML | `xml.etree.ElementTree` | for untrusted input use `defusedxml` |

## A complete example

```python
"""Read a CSV, filter it, write the summary as JSON."""

import csv
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


def summarise_by_recipient(csv_path: Path) -> dict[str, str]:
    totals: defaultdict[str, Decimal] = defaultdict(Decimal)

    with open(csv_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            totals[row["Recipient"]] += Decimal(row["Amount"])

    return {recipient: str(total) for recipient, total in sorted(totals.items())}


def main() -> None:
    summary = summarise_by_recipient(Path("data/transactions.csv"))
    Path("summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
```

Try it against `data/transactions.csv` — that file is real, and you will meet it again in the
projects.

## Check yourself

1. Why must you pass `encoding="utf-8"` explicitly?
2. What does `newline=""` prevent when writing CSV?
3. Why not split a CSV line on commas yourself?
4. What type does `csv.DictReader` give you for a numeric column?
5. Which Python types does `json.dumps` refuse, and how do you handle them?
6. Why is `pickle` unsafe on untrusted input?
