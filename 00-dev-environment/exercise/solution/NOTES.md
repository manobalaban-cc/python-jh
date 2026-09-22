# Reference solution — notes

## Why does `python src/hello_tool/__main__.py Anna` fail?

```
ModuleNotFoundError: No module named 'hello_tool'
```

When you run a **file**, `sys.path[0]` becomes the directory of that file —
`src/hello_tool/`. From there, `hello_tool` is not importable: the importable location is
`src/`, one level up. The `from hello_tool.core import greet` line therefore fails.

The two invocations that do work:

- `python -m hello_tool` — with `-m`, Python imports the package properly through `sys.path`,
  and since the project is installed in editable mode, `src/` is on it.
- `hello-tool` — the console script generated from `[project.scripts]` imports
  `hello_tool.__main__` and calls `main()`, the same way.

**The lesson:** a package is something you import, not a folder of files you run. Entry points
belong in `[project.scripts]` or in `__main__.py`.

## Why `raise SystemExit(main())`?

`main()` returns an exit code instead of calling `sys.exit()` itself. That makes it testable
(you can assert on the return value rather than catching `SystemExit`), while the process still
exits with the right status code for the shell and for CI.

Exit-code convention: `0` success, `1` runtime error, `2` incorrect usage.

## Why `--doctest-modules` in the pytest configuration?

The docstring in `core.py` contains examples in `>>>` form. With this option `pytest` runs them
as tests, so documentation that drifts out of date fails the build. Useful for small, pure
functions; do not try to write whole test suites this way.

## Files that complete the project

`.gitignore`, `.pre-commit-config.yaml` and `.github/workflows/ci.yml` are listed in chapter
[05-git-and-ci.md](../../05-git-and-ci.md); copy them from there.

## The commands the grader will run

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pytest
.venv/Scripts/python -m mypy src/
.venv/Scripts/ruff check .
```

## Why `pytest` fails before you install

```
ModuleNotFoundError: No module named 'hello_tool'
```

The project uses the `src` layout, so the package is only importable once it is installed:

```bash
python -m pip install -e ".[dev]"
pytest
```

That is the point of the layout — the tests import the *installed* package, exactly as a user
would. If you want to run the tests without installing (in CI, say), the escape hatch is
`pytest -o pythonpath=src`, but the install is the honest version.
