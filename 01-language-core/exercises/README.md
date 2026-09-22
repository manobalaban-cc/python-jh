# Exercises — language core

Each task file contains function stubs with a docstring describing the expected behaviour, and
`raise NotImplementedError`. Your job is to make the matching test file pass.

```bash
cd 01-language-core/exercises
python -m pytest -v                                   # everything
python -m pytest tests/test_01_objects_and_types.py -v # one set
python -m pytest -k "counter" -v                       # one test by name
```

| Task file | Covers | Tests |
|---|---|---|
| `tasks/task_01_objects_and_types.py` | chapters 01–02: references, mutability, strings, numbers | `tests/test_01_objects_and_types.py` |
| `tasks/task_02_control_and_collections.py` | chapters 03–04: control flow, list/dict/set/tuple | `tests/test_02_control_and_collections.py` |
| `tasks/task_03_iteration_and_functions.py` | chapters 05–06: comprehensions, generators, closures | `tests/test_03_iteration_and_functions.py` |
| `tasks/task_04_exceptions.py` | chapter 07: exceptions, EAFP, custom errors | `tests/test_04_exceptions.py` |

Reference solutions: `solutions/`. Open them only after you have made a serious attempt —
and even then, compare rather than copy.

## Ground rules

1. **No external libraries.** Standard library only.
2. **Type annotations on everything.** `mypy tasks/` must pass.
3. **`ruff check .` must pass.**
4. Where a task says "without a loop", it means a comprehension or a built-in is expected.

## Difficulty markers

- (basic) — you should get it in a couple of minutes
- (thinking) — there is a trap in it, read the chapter again if stuck
- (junior interview) — this exact question, or a close relative, gets asked in interviews
