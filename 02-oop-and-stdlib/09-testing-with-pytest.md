# 09 — Testing with `pytest`

You know unit testing. This chapter is about the tool: `pytest` is the de-facto standard, and it
looks nothing like JUnit.

## The basics

```python
# tests/test_core.py
from myapp.core import greet


def test_greet_returns_polite_message() -> None:
    assert greet("Anna") == "Hello, Anna!"
```

That is a complete test. No class, no annotation, no `assertEquals` — a plain function whose
name starts with `test_`, in a file named `test_*.py`, using the plain `assert` statement.

`pytest` rewrites assertions so that a failure shows you the values:

```
E       AssertionError: assert 'Hello, anna!' == 'Hello, Anna!'
E         - Hello, Anna!
E         ?        ^
E         + Hello, anna!
```

Running it:

```bash
pytest                        # everything
pytest tests/test_core.py     # one file
pytest -k "greet"             # tests whose name matches
pytest -v                     # one line per test
pytest -x                     # stop at the first failure
pytest --lf                   # only the tests that failed last time
pytest -q --tb=short          # quiet, short tracebacks
pytest --cov=src --cov-report=term-missing
```

## Testing for exceptions

```python
import pytest


def test_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        greet("")
```

`match` is a **regular expression** searched in the message. It stops the test from passing for
the wrong reason.

## Parametrization

Instead of a loop or five near-identical tests:

```python
@pytest.mark.parametrize(
    "score,expected",
    [
        (100, "A"),
        (90, "A"),
        (89, "B"),
        (0, "F"),
    ],
)
def test_grade(score: int, expected: str) -> None:
    assert grade(score) == expected
```

Each row is a separate test case with its own name in the report, so a failure tells you
exactly which input broke.

## Fixtures

A fixture is a named piece of setup, requested by putting its name in the test signature.

```python
import pytest
from pathlib import Path


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "transactions.csv"
    path.write_text(
        "Timestamp,Amount,Currency,Recipient\n"
        "2024-01-01 10:00:00,100.00,EUR,Amazon\n"
        "2024-01-02 11:00:00,250.50,EUR,Spotify\n",
        encoding="utf-8",
    )
    return path


def test_loads_all_rows(sample_csv: Path) -> None:
    rows = load_transactions(sample_csv)
    assert len(rows) == 2
```

Built-in fixtures you will use constantly:

| Fixture | What it gives you |
|---|---|
| `tmp_path` | a fresh `Path` to an empty temporary directory |
| `capsys` | captured stdout/stderr (`capsys.readouterr().out`) |
| `monkeypatch` | temporary patching of attributes, dict entries and env vars |
| `caplog` | captured log records |

```python
def test_reads_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_TIMEOUT", "30")
    assert load_config().timeout == 30        # the variable is removed afterwards
```

Fixtures can set up **and** tear down, using `yield`:

```python
@pytest.fixture
def db_connection() -> Iterator[Connection]:
    conn = connect(":memory:")
    conn.execute("CREATE TABLE tx (id INTEGER, amount REAL)")
    yield conn                 # the test runs here
    conn.close()               # cleanup, even if the test fails
```

Scope controls how often it runs:

```python
@pytest.fixture(scope="session")     # once per test run: expensive resources
@pytest.fixture(scope="module")      # once per test file
@pytest.fixture                      # default: once per test
```

Shared fixtures live in `conftest.py`, which `pytest` loads automatically for every test in
that directory and below. No import needed.

## Mocking

```python
from unittest.mock import Mock, patch


def test_notifies_on_success() -> None:
    notifier = Mock()
    service = ImportService(notifier=notifier)

    service.run(["a", "b"])

    notifier.send.assert_called_once_with("2 records imported")


def test_handles_api_failure() -> None:
    api = Mock()
    api.fetch.side_effect = ConnectionError("down")

    assert load_with_fallback(api) == []
```

`Mock` records everything done to it, and `assert_called_once_with` checks the interaction.
`side_effect` makes it raise, or return a sequence of values on consecutive calls.

Patching something the code imports:

```python
@patch("myapp.core.requests.get")            # patch it WHERE IT IS USED, not where it is defined
def test_fetch(mock_get: Mock) -> None:
    mock_get.return_value.json.return_value = {"rate": 389.5}
    assert fetch_rate("EUR") == 389.5
```

"Patch where it is used" is the rule everyone gets wrong once: if `myapp.core` does
`import requests`, you patch `myapp.core.requests.get`, not `requests.get`.

### What not to mock

Mock the **boundaries** — the network, the clock, the filesystem, third-party services. Do not
mock your own domain objects: a test full of mocks passes happily while the real code is broken,
and it locks the implementation in place so refactoring breaks every test.

The better design is usually dependency injection, which needs no patching at all:

```python
class ImportService:
    def __init__(self, repository: Repository, notifier: Notifier) -> None: ...
```

In a test you pass a small fake class that satisfies the protocol. It is clearer than a `Mock`
and it type-checks.

## Structuring a test

```python
def test_import_skips_invalid_rows(sample_csv: Path) -> None:
    # Arrange
    service = ImportService(repository=InMemoryRepository())

    # Act
    result = service.import_file(sample_csv)

    # Assert
    assert result.imported == 2
    assert result.skipped == 1
```

Guidelines that hold everywhere but bear repeating here:

- **One behaviour per test**, and a name that states it (`test_skips_rows_without_amount`).
- **No logic in tests** — no loops, no ifs; use parametrization instead.
- **Test behaviour, not implementation** — assert on results, not on which private method ran.
- **Tests must be independent** — any order, any subset, no shared mutable state.

## Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers"
markers = [
    "slow: takes more than a second",
    "integration: needs a database",
]
```

```bash
pytest -m "not slow"        # skip the slow ones during development
```

```python
@pytest.mark.slow
def test_full_import() -> None: ...

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX paths only")
def test_symlinks() -> None: ...
```

## Coverage

```bash
pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-report=html      # open htmlcov/index.html
```

Coverage tells you what was **executed**, not what was **verified**. 100% coverage with no
assertions proves nothing. Use it to find untested branches, not as a target to game — for
application code, 70–85% on the parts that matter is a healthy place to be.

## What to test first

1. Pure functions with interesting logic — cheapest to test, highest value.
2. Edge cases: empty input, one element, wrong type, boundary values, duplicates.
3. Error paths: does it raise what it promised?
4. Bugs you fixed — write the failing test first, then fix it. That one never comes back.

## Check yourself

1. What does a `pytest` test need to be discovered?
2. Why is parametrization better than a loop inside a test?
3. What is a fixture, and what does `yield` inside one do?
4. What does `monkeypatch` give you that manual patching does not?
5. Why do you patch "where it is used"?
6. Why is 100% coverage not the goal?
