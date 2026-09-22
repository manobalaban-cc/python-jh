# 01 — Command line, configuration, logging

## `argparse` — in the standard library

```python
import argparse
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="txtool",
        description="Import and summarise transaction exports.",
    )
    parser.add_argument("path", type=Path, help="CSV file to import")
    parser.add_argument("-o", "--output", type=Path, help="write the summary here")
    parser.add_argument("--min-amount", type=float, default=0.0, help="ignore smaller amounts")
    parser.add_argument(
        "--currency",
        choices=["EUR", "USD", "GBP"],
        action="append",
        help="restrict to these currencies (repeatable)",
    )
    parser.add_argument("--dry-run", action="store_true", help="do not write anything")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="-v, -vv")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    return parser.parse_args(argv)
```

`argparse` gives you `--help`, type conversion, validation and error messages for free. Taking
`argv` as a parameter (defaulting to `None`, which means `sys.argv[1:]`) is what makes the
parser testable:

```python
def test_parses_min_amount() -> None:
    args = parse_args(["data.csv", "--min-amount", "100"])
    assert args.min_amount == 100.0
```

Subcommands, when the tool grows:

```python
subparsers = parser.add_subparsers(dest="command", required=True)

import_parser = subparsers.add_parser("import", help="import a file")
import_parser.add_argument("path", type=Path)

report_parser = subparsers.add_parser("report", help="print a summary")
report_parser.add_argument("--format", choices=["text", "json"], default="text")
```

## Typer — nicer, third party

Typer builds the CLI from type annotations, the way FastAPI builds an API:

```python
import typer
from pathlib import Path

app = typer.Typer(help="Import and summarise transaction exports.")


@app.command()
def import_file(
    path: Path,
    min_amount: float = typer.Option(0.0, help="ignore smaller amounts"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Import a CSV export."""
    ...


if __name__ == "__main__":
    app()
```

Use `argparse` when you want zero dependencies, Typer when the CLI is the product.

## The entry point

```python
# src/txtool/__main__.py
import logging
import sys


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose)

    try:
        result = run_import(args.path, min_amount=args.min_amount, dry_run=args.dry_run)
    except SourceError as exc:
        logging.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        logging.warning("interrupted")
        return 130

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Conventions worth following:

- `main()` **returns** an exit code instead of calling `sys.exit()`, so it can be unit-tested.
- Exit codes: `0` success, `1` a runtime failure, `2` incorrect usage (argparse already uses 2),
  `130` interrupted.
- **Results go to stdout, diagnostics to stderr.** That is what makes `txtool report > out.csv`
  work while errors still reach the terminal.
- Register the command in `pyproject.toml` so users get `txtool` instead of `python -m txtool`:

```toml
[project.scripts]
txtool = "txtool.__main__:main"
```

## Logging

```python
import logging
import sys


def configure_logging(verbosity: int = 0) -> None:
    level = {0: logging.WARNING, 1: logging.INFO}.get(verbosity, logging.DEBUG)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)   # quieten chatty libraries
```

In each module:

```python
logger = logging.getLogger(__name__)      # never the root logger
```

Rules, all of which come up in code review:

1. Configure logging **once**, in the entry point. A library that calls `basicConfig` hijacks
   the application's configuration.
2. `logger.info("imported %d rows", n)` — lazy `%s` formatting, not an f-string.
3. `logger.exception(...)` inside an `except` block: it attaches the traceback.
4. Never log secrets, tokens, passwords or full request bodies with personal data.
5. `print()` is for program output; `logging` is for diagnostics. A tool that prints its
   progress into stdout cannot be piped.

Structured logging, when the logs go to a system that indexes them:

```python
logger.info("import finished", extra={"rows": 991, "skipped": 9, "file": str(path)})
```

With `python-json-logger` or `structlog` those fields become JSON keys instead of prose.

## Configuration

Order of precedence, from weakest to strongest — the convention almost every tool follows:

```
defaults in code  <  config file  <  environment variables  <  command-line arguments
```

```python
import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    api_key: str
    timeout: float = 10.0
    batch_size: int = 500

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.environ["DATABASE_URL"],          # required: fail loudly at startup
            api_key=os.environ["API_KEY"],
            timeout=float(os.getenv("TIMEOUT", "10")),
            batch_size=int(os.getenv("BATCH_SIZE", "500")),
        )
```

With Pydantic (see the next chapter) it is shorter and validated:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

    database_url: str
    api_key: str
    timeout: float = 10.0
    batch_size: int = 500


settings = Settings()        # reads .env and the environment, validates types
```

### The rules about secrets

- Secrets come from the environment (or a secret manager), never from the source.
- `.env` is for local development only, and it is in `.gitignore`. `.env.example` is committed.
- Required settings use `os.environ["X"]`, so a missing value crashes at startup rather than
  producing a mysterious `None` three hours into a job.
- A secret that has ever been committed is compromised — rotate it, do not just delete the commit.

## A complete small tool

```python
"""txtool - import a transaction export and print a summary."""

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="txtool", description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--min-amount", type=float, default=0.0)
    parser.add_argument("-v", "--verbose", action="count", default=0)
    return parser.parse_args(argv)


def configure_logging(verbosity: int) -> None:
    level = {0: logging.WARNING, 1: logging.INFO}.get(verbosity, logging.DEBUG)
    logging.basicConfig(level=level, format="%(levelname)-8s %(message)s", stream=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose)

    if not args.path.is_file():
        logger.error("no such file: %s", args.path)
        return 1

    total, count = summarise(args.path, args.min_amount)
    print(f"{count} transactions, total {total:,.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Check yourself

1. Why should `main()` return an exit code instead of calling `sys.exit()`?
2. What belongs on stdout and what on stderr?
3. Where is logging configured, and why not in a library module?
4. What is the usual precedence order between defaults, config files, env vars and CLI flags?
5. Why use `os.environ["X"]` rather than `os.getenv("X")` for a required setting?
6. What do you do about a secret that was committed by mistake?
