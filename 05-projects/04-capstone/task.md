# Project 4 — Capstone: an end-to-end service

**Everything.** This is the piece you show at an interview: a small but complete system that
fetches data, stores it, serves it, reports on it, and ships in a container with CI.

## Choose one

You may pick any of the three, or propose your own with the same shape (external data source →
storage → API → scheduled reporting).

### Option A — Exchange-rate service

Fetch daily rates from a public API (ECB, the Hungarian National Bank, or exchangerate.host),
store the history, and expose:

- `GET /rates/{base}/{quote}?date=...` — the rate on a date (nearest earlier if the market was closed)
- `GET /rates/{base}/{quote}/history?from=...&to=...` — a series with a moving average
- `POST /convert` — convert an amount on a date
- a daily job that fetches yesterday's rates and reports anomalies (a move over 2%)

Uses the real `EUR_HUF_history.csv` as a seed/backfill file.

### Option B — Transaction analytics platform

Extend project 3: the API keeps its endpoints, and you add

- a scheduled job that re-aggregates daily statistics into a summary table,
- `GET /reports/monthly?format=json|csv|md`,
- anomaly detection (a recipient whose spend is 3σ above their own average),
- an endpoint that returns a generated PNG chart.

### Option C — Public-data dashboard

Pick a public API (World Bank, Eurostat, GitHub, transit data). Build an ingestion job, a
normalised store, an API over it, and a small generated HTML report with two charts.

## Mandatory requirements, whichever you choose

### Architecture

1. Three layers with a one-way dependency: `clients/` (outbound I/O) → `domain/` (logic,
   framework-free) ← `api/` and `jobs/` (inbound).
2. Every external dependency is behind a Protocol, so tests use fakes rather than the network.
3. Configuration entirely from the environment; twelve-factor.

### Data

4. Persistent storage (SQLite is fine; PostgreSQL in Docker is better) with migrations.
5. Idempotent ingestion: running it twice changes nothing the second time.
6. Backfill: a command that loads history from a file or by paging the API.

### API

7. At least four endpoints, with validated inputs and consistent errors.
8. `/health` reporting the database and the last successful ingestion.
9. OpenAPI documentation that someone else could integrate against without asking you anything.

### Reliability

10. Retries with backoff for every outbound call, and a timeout on every one of them.
11. Structured logging: every ingestion logs a record with counts and a duration.
12. Errors from the external API never corrupt stored data — partial failures roll back.

### Quality

13. Tests: unit (domain), integration (database), API (TestClient), and one test that proves
    the retry logic works. Coverage above 70% on `domain/`.
14. `ruff`, `mypy --strict` on `domain/`, `pytest` — all green in CI.
15. Dockerfile (multi-stage, non-root) and `docker compose up` that brings the whole thing up.
16. README: what it does, architecture diagram (ASCII is fine), how to run, how to configure,
    what you would do next.

## Timebox

Four to five days. If you are running out of time, cut **scope**, not quality: three endpoints
that are tested, documented and containerised beat eight that are none of those.

## The presentation

Twenty minutes, at the end of the course:

1. **Demo** (5 min) — `docker compose up`, then drive it from the terminal or `/docs`.
2. **Architecture** (5 min) — the layers, and why the boundaries are where they are.
3. **One hard problem** (5 min) — something that did not work, how you diagnosed it, what you
   changed. This is the part people actually remember.
4. **Questions** (5 min) — including "what breaks if the external API is down for a day?" and
   "what would you do with another week?".

## The review checklist

| Area | Question |
|---|---|
| Correctness | Does it do what the README claims? Do the tests actually test it? |
| Architecture | Can you swap the database or the HTTP client without touching the domain? |
| Idiomatic Python | Would a Python developer recognise this as Python, or as Java in disguise? |
| Robustness | What happens on a timeout, a 500, malformed data, an empty response, a duplicate run? |
| Operability | Can someone else run it? Debug it from the logs? Configure it without editing code? |
| Craft | Types, lint, tests, commit history, README. |
