# 03 — Project layout and the import system

This chapter answers the question every developer moving to Python trips over exactly once:
**"why can't my code find my own modules?"**

## Module, package, distribution

| Term | What it is |
|---|---|
| **module** | a single `.py` file. It forms a namespace. |
| **package** | a directory containing modules. An `__init__.py` makes it a "regular" package. |
| **distribution** | what you install from PyPI. Its name is *not necessarily* the importable name (`pip install scikit-learn` → `import sklearn`). |

Java analogy: a module is roughly a file, a package is roughly a `package` — but there is **no
enforced** correspondence between directory structure and fully qualified module name; the
import system resolves that at runtime.

## What happens on `import`?

```python
import myapp.core.parser
```

1. Python checks the **`sys.modules`** cache. If it is already loaded, done — **a module is
   loaded and executed only once per process**.
2. Otherwise it walks **`sys.path`** looking for the `myapp` package.
3. Once found, it **executes the entire module top to bottom** (this is why module-level code
   runs on import!) and stores the result in `sys.modules`.
4. It binds the name in the current namespace.

Two consequences that surprise newcomers:

- **Importing runs code.** A `print()`, a file operation or a network call written at module
  level executes on import. This is why we keep side effects out of module level.
- **Circular imports are a real problem**, because a module is visible in a half-initialised
  state while loading. The fix is almost always restructuring, not a trick.

## `sys.path`

```python
import sys
for p in sys.path:
    print(p)
```

Its content, in order:

1. The **directory of the script being run** (not the working directory!) — for `python -m`, the
   **working directory** instead.
2. Entries from the `PYTHONPATH` environment variable.
3. The standard library directories.
4. The active environment's `site-packages`.

**This is where the classic failure comes from.** Given this layout:

```
project/
├── main.py
└── utils/
    └── helper.py
```

running `python project/main.py` puts `project/` on `sys.path[0]`, so `import utils.helper`
works. But run `main.py` from a different directory, or import it from a test, and it breaks.
**Do not build on this.** The fix: install your own project with `pip install -e .`, and it is
importable from anywhere, always.

## The recommended layout: `src`

```
hello-tool/
├── pyproject.toml          <- the project definition (your pom.xml / package.json)
├── README.md
├── .gitignore
├── src/
│   └── hello_tool/         <- the package itself (underscores, not hyphens!)
│       ├── __init__.py
│       ├── __main__.py     <- entry point for `python -m hello_tool`
│       ├── core.py
│       └── io/
│           ├── __init__.py
│           └── readers.py
└── tests/
    ├── test_core.py
    └── test_readers.py
```

Why `src/`? Because the project root is then **not** on `sys.path`, so your tests import the
**installed** package rather than accidentally the source tree. That catches the classic
"works on my machine, broken for users because a file was left out of the distribution" bug.

## `pyproject.toml`

Since PEP 621 this is the only configuration file you need. (`setup.py` and `setup.cfg` are legacy.)

```toml
[project]
name = "hello-tool"
version = "0.1.0"
description = "Example project for the Python conversion course"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.32",
]

[project.optional-dependencies]
dev = ["pytest>=8.3", "ruff>=0.6", "mypy>=1.11"]

[project.scripts]
hello-tool = "hello_tool.__main__:main"   # becomes a real command on PATH

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.mypy]
strict = true
```

Install for development:

```bash
python -m pip install -e ".[dev]"
```

`-e` (editable) means the package is "installed" but points at your source tree, so a saved
change takes effect immediately. Do this in **every** Python project.

## `__init__.py`, `__main__.py`, and the `__name__` check

**`__init__.py`** — the package initialiser. It is usually empty, but it is also where the
public API is assembled:

```python
# src/hello_tool/__init__.py
from hello_tool.core import parse_log, summarize

__all__ = ["parse_log", "summarize"]
```

**`__main__.py`** — what runs on `python -m hello_tool`.

**`if __name__ == "__main__":`** — Python's most famous boilerplate. Every module has a
`__name__`; it equals `"__main__"` when that file was run directly, and the module's name otherwise.

```python
def main() -> None:
    print("Hello!")

if __name__ == "__main__":
    main()
```

Why does it matter? Because importing executes the module (see above). Without the guard, `main()`
would also run when someone merely wants to import your functions — from a test, for example.

## Absolute vs relative imports

```python
from hello_tool.io.readers import read_csv   # absolute - use this
from .io.readers import read_csv             # relative - acceptable inside a package
from ..core import parse_log                 # parent package - avoid
```

Absolute imports are unambiguous and survive moving code around. Relative imports only work
**inside** a package; run the file as a script and you get
`ImportError: attempted relative import with no known parent package`.

**Never:** star imports (`from module import *`). They hide where a name comes from and can
silently shadow existing names.

## Check yourself

1. What is the difference between a module, a package and a distribution?
2. Why does code run on import, and what does that imply for how you organise code?
3. What is `sys.path[0]` for `python script.py` versus `python -m package`?
4. Why is the `src` layout better than a flat one?
5. What exactly does `pip install -e .` do?
6. Why is the `if __name__ == "__main__":` line needed?
