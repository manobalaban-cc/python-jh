# 04 — IDE, linter, formatter, type checker, debugger

In Python the compiler does **not** catch most of your mistakes, because there is no
compile-time type checking. What `javac` caught for you has to be replaced by tooling.
That is why, in a serious Python project, this toolchain is **mandatory, not optional**.

| Tool | What it does | Java analogy |
|---|---|---|
| `ruff` | linter + formatter in one, written in Rust, very fast | Checkstyle + SpotBugs + formatter |
| `mypy` (or `pyright`) | static type checking based on annotations | the type checking part of `javac` |
| `pytest` | test runner | JUnit |
| `pdb` / IDE debugger | debugging | IDE debugger |

## `ruff` — linter and formatter

```bash
python -m pip install ruff
ruff check .            # find problems
ruff check --fix .      # fix the auto-fixable ones
ruff format .           # format
```

Configuration lives in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E", "W",   # pycodestyle - PEP 8 style
    "F",        # pyflakes - real bugs (unused imports, undefined names)
    "I",        # isort - import ordering
    "UP",       # pyupgrade - modernise old syntax
    "B",        # flake8-bugbear - common logic traps
    "SIM",      # flake8-simplify
]
ignore = ["E501"]   # line length is the formatter's job
```

`ruff` replaces the older `flake8` + `black` + `isort` + `pyupgrade` combination with a single
tool, roughly a hundred times faster. You will still meet those tools in older projects — they
do the same job, just slower and out of four config files.

### PEP 8 — the style convention

Not a suggestion; effectively mandatory. The essentials:

| Element | Convention | Example |
|---|---|---|
| variable, function | `snake_case` | `total_price`, `read_config()` |
| class | `PascalCase` | `TransactionParser` |
| constant | `UPPER_SNAKE` | `MAX_RETRIES` |
| module, package | short, lowercase | `readers.py` |
| "internal" element | leading underscore | `_cache` |
| indentation | **4 spaces**, never tabs | |

Coming from Java or JavaScript, `camelCase` will be muscle memory — `ruff` will tell you.

## `mypy` — static type checking

Python is **dynamically but strongly** typed. Annotations are **not enforced at runtime**:

```python
def double(x: int) -> int:
    return x * 2

double("hi")     # runs! result: "hihi"
```

`mypy` catches that before you commit:

```bash
python -m pip install mypy
mypy src/
```

```
src/app.py:7: error: Argument 1 to "double" has incompatible type "str"; expected "int"
```

To start, this is enough in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true                 # start here in a new project
warn_unreachable = true
```

In an existing, unannotated codebase `strict` would produce thousands of errors; there it is
enabled module by module. Details in
[02-oop-and-stdlib/05-type-hints.md](../02-oop-and-stdlib/05-type-hints.md).

## Setting up VS Code

Extensions: **Python** (Microsoft), **Pylance**, **Ruff**.

`.vscode/settings.json`:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.analysis.typeCheckingMode": "strict",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "editor.codeActionsOnSave": {
    "source.organizeImports.ruff": "explicit"
  }
}
```

The most common VS Code problem is **the wrong interpreter**. `Ctrl+Shift+P` →
`Python: Select Interpreter` → pick the project's `.venv`. If it is not listed, enter the path
manually, then restart the Python Language Server.

`.vscode/launch.json` for debugging:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run module",
      "type": "debugpy",
      "request": "launch",
      "module": "hello_tool",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Current file",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

`justMyCode: false` matters: without it the debugger refuses to step into library code — which
is exactly where you need to go when chasing a pandas or FastAPI problem.

## PyCharm

If you come from IntelliJ you will feel at home. One thing to watch:
`Settings → Project → Python Interpreter`, and add the **existing** `.venv` (do not let it
create its own somewhere else). Community Edition is more than enough for this course.

## Debugging

### `breakpoint()` — the built-in way

Put it anywhere; it works without an IDE:

```python
def process(lines: list[str]) -> int:
    total = 0
    for line in lines:
        breakpoint()          # execution stops here, interactive pdb prompt
        total += int(line)
    return total
```

The `pdb` commands worth memorising:

| Command | Meaning |
|---|---|
| `n` (next) | next line, do not step into calls |
| `s` (step) | step into the call |
| `c` (continue) | run to the next breakpoint |
| `l` (list) | show surrounding source |
| `p expression` | evaluate and print |
| `pp object` | pretty-print |
| `w` (where) | call stack |
| `q` (quit) | quit |

Post-mortem debugging after an exception:

```bash
python -m pdb -c continue app.py     # drops into pdb at the exception
pytest --pdb                          # opens a debugger at the first failing test
```

### With `print`

Nothing wrong with it, but there are two better tools:

```python
print(f"{numbers=}")                  # prints the variable NAME too: numbers=[1, 2, 3]
import logging
logging.debug("processing: %s", line) # can stay in the code, switchable
```

## The mandatory pre-commit sequence

```bash
ruff format .
ruff check --fix .
mypy src/
pytest
```

The next chapter automates this with a pre-commit hook and CI.

## Check yourself

1. Why is "it runs, therefore it is fine" not good enough in Python?
2. What does the annotation in `def f(x: int) -> int:` do at runtime?
3. When is `snake_case` correct and when `PascalCase`?
4. What is the difference between `ruff check` and `ruff format`?
5. What does `print(f"{x=}")` output, and why is it useful?
6. What does `justMyCode: false` mean and when do you need it?
