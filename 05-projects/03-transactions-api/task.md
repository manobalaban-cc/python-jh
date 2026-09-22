# Project 3 — Transactions API

**FastAPI + SQLAlchemy + pytest.** A small service that imports transaction files and serves
them over HTTP.

## The story

The import library you wrote in [module 02](../../02-oop-and-stdlib/exercises/) works, but it
only runs on your laptop. The team wants the imported data available to other services, and the
finance team wants to submit corrections without sending you a CSV.

## Scope

```
POST   /imports                      upload a CSV, import it, return the result
GET    /transactions                 list, filtered and paginated
GET    /transactions/{id}            one transaction
POST   /transactions                 create one manually
PATCH  /transactions/{id}            correct the recipient or the note
DELETE /transactions/{id}            soft delete
GET    /stats/by-recipient           totals per recipient and currency
GET    /stats/monthly                totals per month
GET    /health                       liveness, plus the database status
```

Input file: [`../../data/transactions.csv`](../../data/transactions.csv) — the real one, with
its nine broken rows.

## Requirements

### API

1. **Separate `In` and `Out` Pydantic models.** The client may not set `id`, `created_at` or
   `deleted_at`.
2. **Validation at the boundary**: amount > 0, currency from the supported set, recipient not
   empty, timestamp not in the future. A violation returns **422** with a useful body.
3. **Filtering** on `/transactions`: `currency`, `recipient`, `min_amount`, `max_amount`,
   `from_date`, `to_date`. All optional and combinable.
4. **Pagination**: `limit` (default 50, max 500) and `offset`, and the total count in the
   response.
5. **Correct status codes**: 200, 201 on create, 204 on delete, 404 for a missing id, 422 for
   invalid input, 409 for a conflict (a duplicate import).
6. **Errors are consistent**: every error response has the same shape (`{"detail": ...}`),
   including the ones FastAPI generates.
7. `/docs` is usable: every endpoint has a summary, and the models have examples.

### Import

8. `POST /imports` accepts a file upload, parses it with your module 02 code, and returns
   `{"imported": n, "skipped": m, "errors": [...]}` — the bad rows must not fail the request.
9. Importing the same file twice must not duplicate rows. Define what makes a transaction
   unique, enforce it in the database, and return 409 or a skip count — your choice, documented.
10. The import runs in **one database transaction**: either all the good rows land, or none do.

### Persistence

11. SQLAlchemy 2.0 models: `recipients` and `transactions`, with a foreign key and the indexes
    the filters need.
12. A repository class behind a `Protocol`, so the API layer never touches the session directly.
13. Soft delete: `DELETE` sets `deleted_at`; deleted rows disappear from the list endpoints.
14. No N+1 queries on the list endpoints. Prove it by turning on `echo=True` and counting.

### Quality

15. **Tests**: at least 15, with `TestClient` and an in-memory database, covering every endpoint,
    every error path, filtering, pagination, and the duplicate import.
16. The domain layer imports neither FastAPI nor SQLAlchemy.
17. Configuration from the environment; `.env.example` committed, `.env` not.
18. `ruff`, `mypy`, `pytest` clean in CI.

## Suggested structure

```
transactions-api/
├── pyproject.toml
├── .env.example
├── src/txapi/
│   ├── __main__.py           uvicorn entry point / CLI
│   ├── config.py             Settings (pydantic-settings)
│   ├── api/
│   │   ├── app.py            FastAPI(), routers, exception handlers
│   │   ├── deps.py           get_session, get_repository
│   │   ├── schemas.py        TransactionIn/Out, ImportResult, Page
│   │   └── routes/
│   │       ├── transactions.py
│   │       ├── imports.py
│   │       └── stats.py
│   ├── domain/               models, parsing, validation (from module 02)
│   └── db/
│       ├── models.py         SQLAlchemy models
│       └── repository.py     SqlTransactionRepository
└── tests/
    ├── conftest.py           app + in-memory db fixtures
    ├── test_transactions.py
    ├── test_imports.py
    └── test_stats.py
```

## Hints

- `app.dependency_overrides[get_repository] = ...` swaps the database for a fake in tests.
  Set it in a fixture and clear it afterwards.
- A fresh `sqlite:///:memory:` engine per test keeps them independent. For SQLite in tests with
  a single connection, `StaticPool` and `connect_args={"check_same_thread": False}` save you
  an afternoon.
- `UploadFile` is how FastAPI receives a file; `file.file` is a binary stream, so wrap it with
  `io.TextIOWrapper(file.file, encoding="utf-8")` before handing it to the CSV reader.
- For the pagination response, a generic `Page[T]` Pydantic model keeps it honest:
  `{"items": [...], "total": 1234, "limit": 50, "offset": 0}`.
- A unique constraint on `(timestamp, amount, currency, recipient_id)` is a defensible
  definition of "the same transaction". Say so in the README.
- Index the columns you filter on. Then look at a query plan (`EXPLAIN QUERY PLAN` in SQLite)
  and put the result in your README — that is the kind of evidence reviewers like.

## Acceptance criteria

- [ ] `uvicorn txapi.api.app:app` starts and `/docs` is usable
- [ ] The real `transactions.csv` imports: 991 rows in, 9 reported as errors
- [ ] Importing it twice does not create 1,982 rows
- [ ] Every endpoint has a happy-path test and at least one failure test
- [ ] The domain package has no framework imports (grep for it — that is how it will be checked)
- [ ] No SQL built by string formatting anywhere
- [ ] `pytest`, `mypy src/`, `ruff check .` clean

## Stretch

1. API-key authentication with a `Depends`, and tests for the 401 path.
2. Rate limiting on `/imports`.
3. An async version with `asyncpg` and an async SQLAlchemy session — then measure whether it
   actually helped and write the result in the README.
4. Alembic migrations, including one that adds a column to an existing database.
5. Prometheus metrics on `/metrics`: request count, latency, import counters.
