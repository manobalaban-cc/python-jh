# 07 — Exceptions and error handling

## EAFP, not LBYL

Two philosophies:

- **LBYL** — "Look Before You Leap": check first, then act. The Java/C default.
- **EAFP** — "Easier to Ask Forgiveness than Permission": just do it, handle the failure.
  **This is the Python default.**

```python
# LBYL - carried over from other languages
if "name" in data and data["name"] is not None:
    name = data["name"]
else:
    name = "unknown"

# EAFP - idiomatic Python
try:
    name = data["name"]
except KeyError:
    name = "unknown"

# or simply
name = data.get("name", "unknown")
```

Why does the community prefer EAFP? Two reasons. First, the check-then-act pattern has a race
condition whenever the state can change in between (a file can be deleted between
`os.path.exists` and `open`). Second, exceptions in CPython are cheap: a `try` block that does
not raise costs essentially nothing.

This does not mean "use exceptions for control flow everywhere" — it means you do not have to
defend against every possible failure before acting.

## The exception hierarchy

```
BaseException
├── SystemExit            (sys.exit)
├── KeyboardInterrupt     (Ctrl+C)
├── GeneratorExit
└── Exception             <- everything you should normally catch
    ├── ArithmeticError → ZeroDivisionError, OverflowError
    ├── LookupError      → IndexError, KeyError
    ├── OSError          → FileNotFoundError, PermissionError, TimeoutError, ConnectionError
    ├── RuntimeError     → RecursionError
    ├── ValueError       → UnicodeDecodeError
    ├── TypeError
    ├── AttributeError
    ├── ImportError      → ModuleNotFoundError
    └── StopIteration
```

Catch `Exception`, never `BaseException` — the latter swallows `Ctrl+C` and `sys.exit()`.

The ones you will meet most:

| Exception | Typical cause |
|---|---|
| `ValueError` | right type, wrong value (`int("abc")`) |
| `TypeError` | wrong type (`"a" + 1`) |
| `KeyError` | missing dict key |
| `IndexError` | list index out of range |
| `AttributeError` | attribute does not exist — often means the object is `None` |
| `FileNotFoundError` | the path is wrong (a subclass of `OSError`) |

## `try` / `except` / `else` / `finally`

```python
try:
    connection = connect(url)
    data = connection.fetch()
except TimeoutError as exc:
    logging.warning("timeout: %s", exc)
    data = None
except (ConnectionError, OSError) as exc:      # several types at once
    logging.error("network error: %s", exc)
    raise
else:
    # runs only if NO exception was raised
    logging.info("fetched %d rows", len(data))
finally:
    # always runs - even on return or re-raise
    connection.close()
```

`else` exists so that the `try` block stays minimal: only the statement that can actually raise
goes in it, everything else goes to `else`. That prevents accidentally catching an exception
raised by an unrelated line.

## What not to do

```python
# 1. Bare except - catches SystemExit and KeyboardInterrupt too
try:
    ...
except:              # never
    pass

# 2. Swallowing the error
try:
    process(record)
except Exception:
    pass             # the error is gone with no trace - a debugging nightmare

# 3. Catching too broadly
try:
    value = int(text)
    result = api.call(value)
    save(result)
except Exception:    # which of the three failed? no idea
    ...

# 4. Losing the context
except ValueError:
    raise RuntimeError("processing failed")      # the original traceback is buried
```

The fixes:

```python
# Narrow scope, specific type, logged
try:
    value = int(text)
except ValueError:
    logging.warning("not a number: %r", text)
    return None

# Keep the chain when re-raising
except ValueError as exc:
    raise RuntimeError(f"invalid config value: {text}") from exc

# Deliberately suppressing something harmless
from contextlib import suppress
with suppress(FileNotFoundError):
    Path("cache.tmp").unlink()
```

`raise ... from exc` produces "The above exception was the direct cause of..." in the traceback,
keeping both errors visible. Use `from None` when you deliberately want to hide the original.

## Raising

```python
if amount <= 0:
    raise ValueError(f"amount must be positive, got {amount}")
```

A bare `raise` inside an `except` block re-raises the current exception with its original
traceback — that is how you log and pass on:

```python
except OSError:
    logging.exception("failed to write report")   # logs the full traceback
    raise
```

`logging.exception()` is only valid inside an exception handler; it includes the traceback
automatically.

## Custom exceptions

Define a base exception per package, and derive specific ones from it. Callers can then catch
everything from your library with one `except`.

```python
class ReportError(Exception):
    """Base class for every error raised by this package."""


class SourceUnavailableError(ReportError):
    """The data source could not be reached."""


class InvalidRecordError(ReportError):
    """A record failed validation."""

    def __init__(self, line_no: int, reason: str) -> None:
        super().__init__(f"line {line_no}: {reason}")
        self.line_no = line_no
        self.reason = reason
```

Attach structured data (`line_no`, `reason`) as attributes rather than only formatting it into
the message — the caller may want to act on it.

## Reading a traceback

```
Traceback (most recent call last):
  File "app.py", line 42, in <module>
    main()
  File "app.py", line 30, in main
    report = build_report(rows)
  File "report.py", line 15, in build_report
    total = sum(r["amount"] for r in rows)
  File "report.py", line 15, in <genexpr>
    total = sum(r["amount"] for r in rows)
KeyError: 'amount'
```

Read it **bottom-up**: the last line is the actual error, the frame above it is where it
happened, and the frames above that are how you got there. The deepest frame in *your* code is
where to start looking — frames inside libraries usually mean you passed them something wrong.

Python 3.11+ adds `~~~^^^` markers under the exact sub-expression that failed, which is worth
the upgrade on its own.

## `finally` and resource cleanup

```python
f = open("data.csv", encoding="utf-8")
try:
    process(f)
finally:
    f.close()

# The same thing, idiomatically:
with open("data.csv", encoding="utf-8") as f:
    process(f)
```

The `with` statement (context manager) is the Python equivalent of try-with-resources. Use it
for files, database connections, locks and network sessions. Writing your own is covered in
[02-oop-and-stdlib/07-context-managers-and-decorators.md](../02-oop-and-stdlib/07-context-managers-and-decorators.md).

## Exception groups (3.11+)

When several things fail at once — typically in concurrent code:

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(fetch(url1))
        tg.create_task(fetch(url2))
except* ConnectionError as eg:      # note: except*
    for exc in eg.exceptions:
        logging.error("failed: %s", exc)
```

You will mostly encounter these when using `asyncio.TaskGroup`; writing your own is rare.

## When to raise and when to return

| Situation | What to do |
|---|---|
| The caller broke the contract (invalid argument) | raise `ValueError` / `TypeError` |
| An expected, routine "not found" | return `None` and document it |
| An external system failed | raise a custom, wrapped exception |
| A loop over records, one is bad | log it, count it, continue — do not kill the batch |

## Check yourself

1. What do LBYL and EAFP mean, and which does Python prefer? Why?
2. Why is a bare `except:` dangerous?
3. What does the `else` branch of a `try` statement do, and why is it useful?
4. What is the difference between `raise X from exc` and a plain `raise X`?
5. How do you read a traceback, and where do you start looking?
6. Why is it good practice to give a package its own base exception class?
