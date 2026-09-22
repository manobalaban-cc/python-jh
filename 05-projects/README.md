# 05 — Projects

Four projects of increasing scope. Together they cover everything a junior Python developer is
expected to do unsupervised, and they are deliberately shaped like real tickets: a specification
with acceptance criteria, not a step-by-step recipe.

| # | Project | Skills | Suggested time |
|---|---|---|---|
| [1](01-log-analyser/) | **Log analyser CLI** — standard library only | parsing, collections, generators, dataclasses, CLI, pytest | 1–2 days |
| [2](02-sales-report/) | **Sales report pipeline** — pandas | loading, cleaning, joining, aggregation, charts, reporting | 2–3 days |
| [3](03-transactions-api/) | **Transactions API** — FastAPI + database | API design, validation, persistence, dependency injection, tests | 3–4 days |
| [4](04-capstone/) | **Capstone** — end-to-end service | everything above, plus Docker, CI, scheduling, documentation | 4–5 days |

## How the projects are assessed

Every project is graded on the same five axes. This is also, roughly, what a code review at your
first job will look at.

| Axis | What "good" looks like |
|---|---|
| **Correctness** | it does what the specification says, including the edge cases; the tests prove it |
| **Design** | clear module boundaries; I/O separated from logic; no god functions; no globals |
| **Idiomatic Python** | comprehensions, context managers, dataclasses, exceptions used as the language intends; no patterns carried over from other languages |
| **Robustness** | bad input produces a clear error, not a traceback or a wrong number; nothing is silently swallowed |
| **Craft** | type annotations pass `mypy`; `ruff` is clean; meaningful tests; a README someone else can follow |

## Minimum bar for every project

- [ ] `pyproject.toml`, `src/` layout, editable install
- [ ] runs from a clean clone with two commands
- [ ] `ruff check .`, `ruff format --check .`, `mypy src/`, `pytest` all pass
- [ ] test coverage on the logic (not the I/O plumbing) above ~70%
- [ ] a README stating what it does, how to run it, how to configure it and what it assumes
- [ ] no secrets, no `.venv`, no `__pycache__` in the repository
- [ ] meaningful commit history — not one commit called "final"

## Presenting your work

Each project ends with a 10-minute walkthrough:

1. Demonstrate it running. (Not slides — the terminal.)
2. Walk through one design decision and the alternative you rejected.
3. Show the test you are proudest of, and one case you deliberately did not handle.
4. Answer: "what would you do differently with another two days?"

The ability to explain and defend a decision is exactly what separates a junior who can be
given a ticket from one who cannot.
