# 04 — Building applications

So far you have written code. This module is about shipping it: a command-line tool with
configuration and logging, a web API, a database layer, concurrency where it helps, and the
packaging and CI that put it on someone else's machine.

| Chapter | Topic |
|---|---|
| [01](01-cli-and-configuration.md) | `argparse`, Typer, logging, configuration, secrets, exit codes |
| [02](02-fastapi-and-pydantic.md) | Pydantic v2 validation, FastAPI, dependency injection, testing an API |
| [03](03-databases.md) | `sqlite3`, SQLAlchemy 2.0 Core and ORM, migrations, transactions |
| [04](04-concurrency.md) | The GIL revisited: threads, processes, `asyncio` — and which to choose |
| [05](05-packaging-and-deployment.md) | Packaging, entry points, Docker, GitHub Actions, environments |
| [06](06-performance-and-profiling.md) | Measuring before optimising: `timeit`, `cProfile`, memory, common wins |
| [exercises/](exercises/) | A complete service: API + database + tests + container |

## By the end of this module

- You can turn a script into a proper CLI with arguments, configuration and logging.
- You can build a small REST API with validated request and response models, and test it
  without starting a server.
- You can talk to a database from Python without string-concatenating SQL.
- You can say, for a given slow task, whether threads, processes or async is the answer — and why.
- You can containerise a Python application and run its tests in CI.

## The shape of a real Python application

```
myservice/
├── pyproject.toml
├── Dockerfile
├── .env.example
├── src/myservice/
│   ├── __init__.py
│   ├── __main__.py        # CLI entry point
│   ├── config.py          # settings, read from the environment
│   ├── api/               # FastAPI routers - the HTTP layer only
│   ├── domain/            # business logic - no framework imports here
│   ├── db/                # models, repositories, migrations
│   └── clients/           # outbound HTTP, message queues
└── tests/
    ├── unit/
    └── integration/
```

The important boundary is `domain/`: it contains no FastAPI, no SQLAlchemy and no `requests`.
That is what keeps the business rules testable in milliseconds and independent of the
frameworks around them.
