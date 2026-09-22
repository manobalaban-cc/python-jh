# Exercise — environment and project skeleton

**Goal:** build a complete Python project from an empty folder, and leave it in a state where a
colleague can run it with two commands.

You will reuse this skeleton throughout the course — every project looks like this. It is worth
memorising the steps.

## Task 1 — create the project

Create a project called `hello-tool` with this structure:

```
hello-tool/
├── pyproject.toml
├── README.md
├── .gitignore
├── .pre-commit-config.yaml
├── src/hello_tool/
│   ├── __init__.py
│   ├── __main__.py
│   └── core.py
└── tests/
    └── test_core.py
```

Requirements:

- `python -m venv .venv` plus activation (or `uv venv`)
- `python -m pip install -e ".[dev]"` runs cleanly
- `pyproject.toml` declares a `dev` extra: `pytest`, `ruff`, `mypy`
- `[project.scripts]` registers a `hello-tool` command
- it is a Git repository with an initial commit

## Task 2 — the code

`core.py` contains:

```python
def greet(name: str, shout: bool = False) -> str:
    """Return a greeting.

    >>> greet("Anna")
    'Hello, Anna!'
    >>> greet("Anna", shout=True)
    'HELLO, ANNA!'
    """
```

`__main__.py` is the command-line entry point: it takes the name as an argument (`sys.argv` is
fine here, `argparse` comes in module 04) and prints the greeting.

Verify that **all three** invocation styles behave as expected:

```bash
python -m hello_tool Anna
hello-tool Anna                            # thanks to [project.scripts]
python src/hello_tool/__main__.py Anna     # why does this one FAIL? explain it
```

## Task 3 — tests

Write `tests/test_core.py` covering both branches (shout / no shout). `pytest` must run from the
project root with no extra configuration.

## Task 4 — quality gate

- `ruff check .` and `ruff format --check .` pass
- `mypy src/` passes in strict mode
- after `pre-commit install`, a deliberately badly formatted commit **fails**

## Task 5 — CI

Push it to GitHub and add an Actions workflow that runs lint + type check + tests on push.
Put the build badge in the README.

## Self-assessment

- [ ] After a fresh clone, `pip install -e ".[dev]"` followed by `pytest` passes
- [ ] `.venv` is **not** in the repository
- [ ] No `__pycache__` in the repository
- [ ] `sys.executable` points at the project `.venv`
- [ ] You can explain why the third invocation in task 2 fails

A complete reference solution lives in [solution/](solution/) — look at it only after you have
struggled with it yourself.
