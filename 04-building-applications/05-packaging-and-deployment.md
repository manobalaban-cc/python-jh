# 05 — Packaging, containers, CI

## Packaging with `pyproject.toml`

```toml
[project]
name = "myservice"
version = "1.2.0"
description = "Transaction import service"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "you@example.com" }]

dependencies = [
    "fastapi>=0.115",
    "pydantic>=2.9",
    "SQLAlchemy>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.3", "pytest-cov", "ruff", "mypy", "httpx"]

[project.scripts]
myservice = "myservice.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/myservice"]
```

Build backends are interchangeable: `hatchling` (a good default), `setuptools` (the classic),
`flit` (minimal), `poetry-core`, `maturin` (for Rust extensions).

Building and publishing:

```bash
python -m pip install build twine
python -m build                       # produces dist/*.whl and dist/*.tar.gz
twine check dist/*
twine upload --repository testpypi dist/*     # try TestPyPI first
twine upload dist/*
```

Version numbers follow semantic versioning: `MAJOR.MINOR.PATCH`, where MAJOR means "I broke
something on purpose".

### Application vs library

| | Library | Application |
|---|---|---|
| Dependency bounds | loose (`pandas>=2.2`) | pinned via a lockfile |
| Distribution | wheel on PyPI | container image, or a wheel plus a lockfile |
| Python versions | test on several | one, the one you deploy |
| Entry points | maybe | almost always |

## Docker

```dockerfile
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy only the dependency metadata first: this layer is cached until it changes,
# so a code-only change does not reinstall the world.
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .


FROM python:3.12-slim

RUN useradd --create-home --uid 1000 app       # do not run as root
WORKDIR /app
USER app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "myservice.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

`.dockerignore`:

```
.venv/
__pycache__/
.git/
.pytest_cache/
.mypy_cache/
tests/
*.md
.env
```

The four things that matter in a Python image:

1. **Multi-stage build** — build dependencies do not ship.
2. **Layer order** — dependencies before source, so the expensive layer stays cached.
3. **`PYTHONUNBUFFERED=1`** — otherwise your logs vanish into a buffer and appear late (or never,
   if the container is killed).
4. **A non-root user.**

```bash
docker build -t myservice:1.2.0 .
docker run --rm -p 8000:8000 --env-file .env myservice:1.2.0
```

`docker compose` for the service plus its database:

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+psycopg://app:secret@db:5432/app
    depends_on: [db]

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    volumes: ["pgdata:/var/lib/postgresql/data"]

volumes:
  pgdata:
```

## CI with GitHub Actions

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - run: python -m pip install -e ".[dev]"
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy src/
      - run: pytest --cov=src --cov-report=xml --cov-fail-under=70

  docker:
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myservice:${{ github.sha }} .
```

A good pipeline fails fast and in a useful order: lint (seconds) → types (seconds) → unit tests
(seconds) → integration tests (minutes) → build.

## Environments and the twelve-factor habits

- **Configuration comes from the environment**, so the same image runs in dev, staging and
  production with different variables.
- **No secrets in the image**, in the repository, or in the logs.
- **Logs go to stdout/stderr**, not to files the container will lose. The platform collects them.
- **The application is stateless**; state lives in the database or object storage.
- **A health endpoint** (`/health`) so the orchestrator knows when to restart or route traffic.
- **Graceful shutdown**: handle `SIGTERM`, finish the in-flight request, close connections.

## Dependency hygiene

```bash
python -m pip list --outdated
python -m pip install pip-audit && pip-audit      # known vulnerabilities
```

Enable Dependabot or Renovate to raise update PRs. The point of the lockfile plus a test suite
is that you can take those updates routinely instead of being three major versions behind when
a CVE forces you.

## Check yourself

1. What is the difference between how a library and an application handle dependency versions?
2. Why copy `pyproject.toml` into the image before the source code?
3. What does `PYTHONUNBUFFERED=1` fix?
4. Why must configuration come from the environment rather than a file in the image?
5. In what order should a CI pipeline run its checks, and why?
6. What does a health endpoint give you?
