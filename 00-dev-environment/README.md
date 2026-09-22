# 00 — Development environment

In Java you had the JDK plus Maven/Gradle; in .NET the SDK plus NuGet; in Node, `npm`.
In Python this layer is, for historical reasons, **fragmented**: several tools do the same
job, each from a different era. This module tells you which one to use and why.

| Chapter | Topic |
|---|---|
| [01](01-interpreter-and-versions.md) | The interpreter, versions, the `py` launcher, what CPython actually is |
| [02](02-virtual-environments.md) | `venv`, `pip`, `uv`, dependency management, lockfiles |
| [03](03-project-layout-and-imports.md) | `pyproject.toml`, package layout, the import system |
| [04](04-ide-linting-debugging.md) | VS Code / PyCharm, `ruff`, `mypy`, formatting, debugging |
| [05](05-git-and-ci.md) | `.gitignore`, pre-commit, GitHub Actions |
| [exercise/](exercise/) | Build a complete project skeleton from scratch |

## By the end of this module

- You can turn an empty folder into a working, tested, linted Python project in five minutes.
- You understand why you must never `pip install` into the system Python.
- You know exactly what happens on `import`, and why your code cannot find your own modules.
