# 05 — Git, pre-commit and CI in a Python project

You already know Git, so this chapter only covers what is **Python-specific**.

## `.gitignore`

What never gets committed:

```gitignore
# Virtual environment
.venv/
venv/

# Bytecode cache
__pycache__/
*.py[cod]
*.so

# Build and packaging artefacts
build/
dist/
*.egg-info/

# Tool caches
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Secrets and local configuration
.env
*.local.toml

# IDE
.idea/
.vscode/*
!.vscode/settings.json
!.vscode/launch.json

# Data (decide by size)
*.parquet
data/raw/
```

GitHub's `github/gitignore` repository has an official `Python.gitignore` — start from that.

> **The `.env` file never enters the repository.** Commit a `.env.example` instead, with the
> keys present but the values blank, so a colleague knows what to configure.

## Commit or not — the summary

| File | Commit? | Why |
|---|---|---|
| `pyproject.toml` | yes | it is the project definition |
| `uv.lock` / `requirements.txt` | yes | reproducible environment |
| `.venv/` | **no** | machine-specific, full of absolute paths |
| `__pycache__/` | **no** | generated |
| `.env` | **no** | contains secrets |
| `.env.example` | yes | documents the required variables |
| small test data | yes | the tests depend on it |

## `pre-commit`

`pre-commit` is a framework for Git hooks: before each commit it runs your linters and
formatters, and fails the commit if something is wrong.

```bash
python -m pip install pre-commit
pre-commit install          # wires up .git/hooks/pre-commit
```

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
      - id: detect-private-key

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

Run it across the whole repository once (useful when introducing it):

```bash
pre-commit run --all-files
```

## CI — GitHub Actions

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e ".[dev]"

      - name: Lint
        run: ruff check .

      - name: Check formatting
        run: ruff format --check .

      - name: Type check
        run: mypy src/

      - name: Tests
        run: pytest --cov=src --cov-report=term-missing
```

The **matrix** is not decoration: there are real behavioural differences between Python
versions, and testing on every supported version is the minimum bar for a library.

## Branching and commit habits

Nothing Python-specific here — feature branch, PR, review, merge as usual. But three review
comments come up constantly in Python projects:

- **do not commit commented-out code** — Git already remembers what was there;
- **do not commit `print()` debugging** — that is what `logging` is for;
- **do not mix formatting with logic changes** in one commit — introduce `ruff format` in its
  own commit so reviews stay readable.

## Check yourself

1. Why do we not commit `.venv`, and what do we commit instead?
2. What is the difference between `.env` and `.env.example`?
3. What does `pre-commit install` do?
4. Why does CI run the tests on several Python versions?
