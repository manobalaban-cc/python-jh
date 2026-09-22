# Module project — `txlib`, a small import library

Instead of a set of disconnected exercises, this module has one coherent task: build a small
library the way a real internal library is built. Every topic of the module appears in it.

You are given: the **specification** (this file), the **tests** (`tests/`) and a **skeleton**
(`src/txlib/`). You write the implementation. A complete reference implementation is in
`solution/` — use it to compare afterwards.

```bash
cd 02-oop-and-stdlib/exercises
python -m pip install -e ".[dev]"
python -m pytest -v
```

## What the library does

`txlib` loads bank transactions from a CSV file, validates them, converts them into domain
objects and hands them to a repository. Input file:
[`../../data/transactions.csv`](../../data/transactions.csv).

```
Timestamp,Amount,Currency,Recipient
2024-04-27 13:59:08.985760,815.85,GBP,Amazon
```

## The pieces

### 1. `txlib/models.py` — the domain (chapters 01–03)

```python
class Currency(StrEnum)                 # EUR, USD, GBP, JPY, CAD, HUF
```

```python
@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: Currency
```

- Rejects a negative amount in `__post_init__` with `ValueError`.
- `__str__` gives `"815.85 GBP"` (two decimals, thousands separator: `1,234.50 EUR`).
- Supports `+` between the same currency; different currencies raise `ValueError`.
- Supports `*` by an `int` or `Decimal`, in both orders (`money * 2` and `2 * money`).
- Being frozen, it is hashable and usable as a dict key.

```python
@dataclass(frozen=True, slots=True)
class Transaction:
    timestamp: datetime
    money: Money
    recipient: str
```

- `is_large(threshold)` returns whether the amount reaches the threshold (default 1000).
- Sorts by timestamp (`sorted()` on a list of transactions must work).

### 2. `txlib/errors.py` — the exception hierarchy (chapter 01-language-core/07)

```
TxError                   base for everything the library raises
├── ValidationError       one field of one row is wrong; has .field, .reason, .row_number
└── SourceError           the file could not be read or is missing its header
```

### 3. `txlib/parsing.py` — row to object (chapters 03, 08)

```python
def parse_row(row: Mapping[str, str], row_number: int) -> Transaction
```

- Missing or empty field → `ValidationError` naming that field.
- Unparseable timestamp or amount → `ValidationError` with the original error as `__cause__`.
- Unknown currency → `ValidationError` listing the accepted values.
- Recipient is stripped of whitespace; an empty recipient is an error.

### 4. `txlib/repository.py` — storage (chapter 04)

```python
class Repository(Protocol):
    def add(self, transaction: Transaction) -> None: ...
    def all(self) -> list[Transaction]: ...
    def totals_by_recipient(self) -> dict[tuple[str, Currency], Money]: ...
```

Plus `InMemoryRepository`, an implementation that satisfies it. No inheritance from the
protocol — that is the point of structural typing.

The summary is keyed by `(recipient, currency)` on purpose: the real dataset has several
currencies per recipient, and adding GBP to JPY is not a thing. Let the type say so.

### 5. `txlib/loading.py` — the use case (chapters 07, 08)

```python
@dataclass
class ImportResult:
    imported: int
    skipped: int
    errors: list[ValidationError]

def load_file(path: Path, repository: Repository) -> ImportResult
```

- Missing file → `SourceError` (not `FileNotFoundError`), chained from the original.
- A file whose header lacks the required columns → `SourceError`.
- One bad row must **not** abort the import: count it, keep its error, carry on.
- The file must be read in a streaming fashion (do not load it all into memory).

### 6. `txlib/instrumentation.py` — cross-cutting concerns (chapter 07)

```python
@timed                                  # decorator: logs "<name> took 0.123 s" at INFO
class Timer(label: str)                 # context manager: .elapsed after the block
```

`@timed` must preserve the wrapped function's `__name__` and `__doc__`.

## Definition of done

- [ ] `python -m pytest` — all green
- [ ] `mypy src/ --strict` — clean
- [ ] `ruff check .` and `ruff format --check .` — clean
- [ ] Every public function and class has an annotation and a docstring
- [ ] `python -m txlib ../../data/transactions.csv` prints a summary of the real dataset

## Stretch goals

1. Add `total_by_currency()` to the repository and a matching test.
2. Make `load_file` accept an open file object as well as a path (hint: `Protocol` with `read`).
3. Add a `--min-amount` filter to the CLI and test it with `capsys`.
4. Write a `CsvRepository` that satisfies the same protocol and writes rows back out to disk.
   Note that the tests for `InMemoryRepository` should pass for it too — parametrize the fixture.
