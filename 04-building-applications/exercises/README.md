# Exercises — build the service

One build, five milestones. Each milestone is a working state you can commit; together they add
up to the kind of service a junior is expected to be able to produce and defend in review.

Start from the transaction domain you already built in
[module 02](../../02-oop-and-stdlib/exercises/) — reuse the parsing and validation code.

```bash
mkdir txservice && cd txservice
python -m venv .venv && .venv/Scripts/activate
python -m pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy pytest httpx ruff mypy
```

## Milestone 1 — the CLI

`python -m txservice import data/transactions.csv --min-amount 100 -v`

- [ ] `argparse` with `path`, `--min-amount`, `--dry-run`, `-v/-vv`, `--version`
- [ ] `main(argv=None) -> int`, tested by calling it with a list of arguments
- [ ] logging configured in the entry point only; `-v` controls the level
- [ ] results on stdout, diagnostics on stderr
- [ ] exit codes: 0 / 1 / 2
- [ ] `[project.scripts]` registers the `txservice` command

## Milestone 2 — configuration

- [ ] a `Settings` model (`pydantic-settings` or a frozen dataclass) covering
      `DATABASE_URL`, `API_KEY`, `BATCH_SIZE`, `LOG_LEVEL`
- [ ] read from the environment, with `.env` support for local development
- [ ] `.env.example` committed, `.env` ignored
- [ ] missing required settings fail at startup with a clear message
- [ ] a test that sets an environment variable with `monkeypatch` and asserts the effect

## Milestone 3 — persistence

- [ ] SQLAlchemy 2.0 models: `recipients` and `transactions`, with a foreign key
- [ ] a `TransactionRepository` protocol, with SQL and in-memory implementations
- [ ] the import command writes to the database, in one transaction per file
- [ ] re-importing the same file does not duplicate rows (define and enforce a key)
- [ ] tests run against `sqlite:///:memory:` with a fresh schema per test

## Milestone 4 — the API

```
GET  /health
GET  /transactions?currency=EUR&min_amount=100&limit=50
GET  /transactions/{id}
POST /transactions
GET  /stats/by-recipient
```

- [ ] separate `TransactionIn` and `TransactionOut` models
- [ ] 404 for a missing id, 422 for invalid input, 201 for a successful create
- [ ] the repository arrives through `Depends`, and tests override it
- [ ] pagination with `limit`/`offset`, and a sane maximum
- [ ] tests with `TestClient` covering the happy path and at least three failure paths
- [ ] `/docs` shows sensible schemas and examples

## Milestone 5 — ship it

- [ ] multi-stage `Dockerfile`, non-root user, `PYTHONUNBUFFERED=1`, healthcheck
- [ ] `docker compose` with the API and a PostgreSQL service
- [ ] GitHub Actions: ruff → mypy → pytest → docker build
- [ ] `README.md`: what it does, how to run it, how to configure it, how to test it

## Stretch

1. Fetch daily exchange rates from a public API and expose totals converted to EUR
   (with a timeout, `raise_for_status`, retries and a cache).
2. Import several files concurrently — measure whether threads actually help, and explain the
   result in terms of the GIL.
3. Add Alembic and turn the schema into a migration.
4. Add `/stats/monthly` backed by a SQL `GROUP BY`, and compare its timing against doing the
   same aggregation in pandas.

## What review will look at

- Is the domain logic free of FastAPI and SQLAlchemy imports?
- Is every SQL statement parameterised?
- Are there tests for the failure paths, not just the happy path?
- Is any secret in the repository? (An automatic fail.)
- Does `docker run` work on a machine that has never seen the project?
