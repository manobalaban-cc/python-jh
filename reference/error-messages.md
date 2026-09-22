# Reading Python errors

## How to read a traceback

```
Traceback (most recent call last):
  File "app.py", line 42, in <module>
    main()
  File "app.py", line 30, in main
    report = build_report(rows)
  File "report.py", line 15, in build_report
    total = sum(r["amount"] for r in rows)
                ~~~~~~~~~~~
KeyError: 'amount'
```

1. **Read the last line first** — that is the actual error.
2. **Read upwards** — each frame is the caller of the one below it.
3. **Find the deepest frame in *your* code.** If the deepest frames are inside a library, you
   almost certainly passed it something wrong.
4. **Python 3.11+ underlines the exact sub-expression** that failed. Use it.
5. For a chained exception, look for the `during handling of the above exception` /
   `the direct cause of` line: there are two errors, and the first one is usually the real one.

## The errors you will actually meet

| Message | What it means | Usual cause |
|---|---|---|
| `NameError: name 'x' is not defined` | the name does not exist here | typo, or used before assignment, or a missing import |
| `UnboundLocalError: local variable 'x' referenced before assignment` | you assign to `x` somewhere in the function, so it is local everywhere in it | needs `global`/`nonlocal`, or a different name |
| `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | strong typing bites | a value came from `input()` or a CSV and is still a string |
| `TypeError: 'NoneType' object is not subscriptable` | you indexed `None` | a function returned `None` — often one that mutates in place, like `list.sort()` |
| `TypeError: 'NoneType' object is not iterable` | you iterated `None` | same as above |
| `AttributeError: 'NoneType' object has no attribute 'x'` | Python's null-pointer error | the same again; find what returned `None` |
| `AttributeError: 'list' object has no attribute 'split'` | wrong type in hand | you have a list where you expected a string |
| `KeyError: 'amount'` | the dict key is missing | typo, case difference, or the data is not what you assumed — use `.get()` if it is optional |
| `IndexError: list index out of range` | index past the end | empty list, or an off-by-one |
| `ValueError: invalid literal for int() with base 10: 'abc'` | right type, wrong value | unvalidated input |
| `ValueError: too many values to unpack` | unpacking mismatch | the row has more columns than you expected |
| `ZeroDivisionError` | division by zero | an empty collection in an average |
| `ModuleNotFoundError: No module named 'pandas'` | not installed **in this interpreter** | wrong virtual environment |
| `ImportError: cannot import name 'x' from 'y'` | the name is not there | typo, version difference, or a circular import |
| `ImportError: attempted relative import with no known parent package` | you ran a package file as a script | use `python -m package` |
| `IndentationError` / `TabError` | mixed or wrong indentation | tabs and spaces mixed; let the formatter fix it |
| `RecursionError: maximum recursion depth exceeded` | runaway recursion | a missing base case; Python does not optimise tail calls |
| `FileNotFoundError: [Errno 2] ...` | the path is wrong | a relative path plus a different working directory; print `Path.cwd()` |
| `PermissionError: [Errno 13]` | no access | the file is open in Excel, or you are writing to a protected folder |
| `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe1` | the file is not UTF-8 | pass the real encoding (`cp1250`, `latin-1`) or `errors="replace"` |
| `JSONDecodeError: Expecting value: line 1 column 1` | the body is not JSON | an HTML error page from a failed HTTP call — you skipped `raise_for_status()` |
| `RuntimeError: dictionary changed size during iteration` | mutating while iterating | iterate over `list(d.items())`, or build a new dict |
| `RuntimeWarning: coroutine 'x' was never awaited` | you called an async function without `await` | add `await`, or `asyncio.run()` |
| `SyntaxError: invalid syntax` pointing at a line that looks fine | the real problem is on the **previous** line | an unclosed bracket or quote |

## pandas-specific messages

| Message | Meaning |
|---|---|
| `ValueError: The truth value of a Series is ambiguous` | you used `and`/`or`/`if` on a Series — use `&`/`\|` with parentheses |
| `KeyError: 'Amount'` on a DataFrame | the column does not exist — check `df.columns` for whitespace or case |
| `SettingWithCopyWarning` (pandas 2) / `ChainedAssignmentError` (pandas 3) | chained assignment — use `df.loc[mask, "col"] = ...` |
| `TypeError: '>' not supported between instances of 'str' and 'int'` | the column is text, not numeric — `pd.to_numeric(..., errors="coerce")` |
| `MergeError: Merge keys are not unique` | your `validate=` assumption was wrong — good, it caught a bug |
| `ValueError: cannot reindex on an axis with duplicate labels` | duplicate index values — `reset_index(drop=True)` |

## When the error is not where it seems

- **Generators**: the exception surfaces where the generator is *consumed*, not where it was
  created.
- **Decorators**: without `functools.wraps` the traceback shows `wrapper` everywhere.
- **Threads and async**: an exception in a task may only appear when someone calls `.result()`.
- **Import time**: an error during import shows the importing module's frame, not the caller's.

## Tools that shorten the hunt

```python
breakpoint()                      # stop here and look around
print(f"{value=} {type(value)=}") # the fastest possible check
import traceback; traceback.print_exc()
logging.exception("context")      # the traceback plus your message
```

```bash
python -X dev script.py           # development mode: more warnings
python -m pdb -c continue app.py  # drop into the debugger at the exception
pytest --pdb                      # same, for the first failing test
pytest -x -l                      # stop at the first failure, show local variables
```

## The habit that matters

**Read the error before changing anything.** It names the type, the value, the file, the line
and usually the exact expression. Most of the time the message is not cryptic — it is precise,
and it has already told you what is wrong.
