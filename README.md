# Python for Working Developers

## Structure

| Module | Topic |
|---|---|
| [00 — Development environment](00-dev-environment/) | Interpreter, versions, `venv`/`uv`, packaging, project layout, IDE, linter, debugger |
| [01 — Language core](01-language-core/) | Execution and object model, types, collections, iteration, functions, exceptions |
| [02 — OOP, data model, stdlib](02-oop-and-stdlib/) | Classes, dunder methods, dataclasses, protocols, typing, generators, decorators, stdlib, pytest |
| [03 — Data toolkit](03-data-toolkit/) | NumPy, pandas (basics, cleaning, groupby, joins, reshaping), matplotlib/seaborn, HTTP APIs |
| [04 — Building applications](04-building-applications/) | CLI, logging, configuration, FastAPI + Pydantic, SQLAlchemy, concurrency, packaging, Docker, CI |
| [05 — Projects](05-projects/) | Four graded projects of increasing scope |

Supporting material:

- [reference/from-java-csharp.md](reference/from-java-csharp.md) — migration cheat sheet from Java/C#/JS
- [reference/pythonic-idioms.md](reference/pythonic-idioms.md) — the 30 most common non-Pythonic patterns and their fixes
- [reference/error-messages.md](reference/error-messages.md) — typical tracebacks and what they actually mean
- [reference/junior-checklist.md](reference/junior-checklist.md) — self-assessment checklist (also useful before interviews)
- [reference/extra-practice.md](reference/extra-practice.md) — katas, books and documentation worth reading
- [reference/instructor-guide.md](reference/instructor-guide.md) — schedule, contact-session scripts, assessment
- [data/](data/) — every dataset used in the exercises and projects ([notes](data/README.md))

## Prerequisites

- Python **3.12 or newer** (we use 3.10+ syntax: `match`, `X | Y` type unions)
- Git
- VS Code or PyCharm
- A terminal you are not afraid of

Step-by-step setup: [00-dev-environment/01-interpreter-and-versions.md](00-dev-environment/01-interpreter-and-versions.md)

## Getting started in 60 seconds

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
pytest --version
```

## How to use this material

Every chapter follows the same shape:

1. **Theory** — why it works this way, what happens under the hood. Do not skip it: this is
   exactly what junior interviews probe (*"what is the difference between a list and a tuple,
   and why does it matter?"*).
2. **Code** — runnable examples. Type them out, do not copy-paste.
3. **Exercises** — in the `exercises/` folder, verified with `pytest`.
4. **Check yourself** — if you cannot answer a question, re-read the chapter.

The exercises are plain **`.py` files, not notebooks**. You work in the same setup you would
work in on a real project: virtual environment, `pyproject.toml`, `pytest`, linter, debugger.

## Learning outcomes

By the end of the course you can:

- set up a Python project from scratch (virtual environment, dependencies, package layout, entry point);
- write idiomatic Python and recognise patterns carried over from other languages;
- explain the execution and object model (reference semantics, mutability, the GIL, name resolution);
- write type-annotated code that passes `mypy`;
- write unit tests, parametrized tests and mocks with `pytest`;
- load, clean, aggregate, join and visualise real, messy data with `pandas`;
- consume REST APIs and serve one with FastAPI backed by a database;
- package an application, containerise it and run it in CI.