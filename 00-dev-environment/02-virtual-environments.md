# 02 — Virtual environments and package management

## The problem

With Maven/Gradle/npm, dependencies are resolved **per project** (`~/.m2`, `node_modules`), and
the build tool makes sure each project sees its own versions.

Python's `import`, by contrast, uses a **global search path**. If you just install a package, it
lands next to the **Python installation**, and **every** project on the machine sees it. Two
projects needing `pandas 1.5` and `pandas 2.2` are mutually exclusive.

The solution is a **virtual environment**: a directory containing its own `site-packages` and a
thin redirection to the base interpreter. One per project.

## `venv` — the built-in answer

```bash
python -m venv .venv          # create it (the name .venv is the convention)
```

What you get:

```
.venv/
├── Scripts/            (Windows)  |  bin/  (macOS, Linux)
│   ├── python.exe                 |  python
│   ├── pip.exe                    |  pip
│   └── activate                   |  activate
├── Lib/site-packages/             |  lib/python3.12/site-packages/
└── pyvenv.cfg                     <- points at the base interpreter
```

Activation:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows cmd
.venv\Scripts\activate.bat
# macOS / Linux
source .venv/bin/activate
```

If PowerShell refuses with `running scripts is disabled`:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Leave with `deactivate`.

### What does activation actually do?

Nothing magical: it prepends `.venv/Scripts` (or `bin`) to `PATH` and sets a couple of
environment variables (`VIRTUAL_ENV`). Which means **everything works without activation** too,
if you use the full path:

```bash
.venv/Scripts/python.exe -m pip install requests
```

That knowledge is worth a lot in CI, in Docker and in VS Code, where there is no interactive shell.

### Verifying

```python
import sys
print(sys.executable)   # which interpreter is running
print(sys.prefix)       # which environment we are in
```

If `sys.prefix` points at your project's `.venv`, you are in the right place.

> **Never commit `.venv`.** It is not portable (it contains absolute paths) and it is large.
> It goes into `.gitignore`. What you commit is the **dependency list**.

## `pip` — the installer

```bash
python -m pip install requests              # latest version
python -m pip install "pandas>=2.2,<3"      # version range
python -m pip install -r requirements.txt   # from a list
python -m pip install -e .                  # your own project, editable mode
python -m pip list                          # what is installed
python -m pip show pandas                   # details, dependencies
python -m pip uninstall pandas
```

Packages come from **PyPI** (pypi.org) — the equivalent of Maven Central or the npm registry.
Two package formats exist:

- **wheel** (`.whl`) — a pre-built binary; fast to install. This is what you get almost always.
- **sdist** (`.tar.gz`) — source, compiled on your machine. If an install suddenly demands a
  C compiler, it is because no wheel exists for your platform/version.

### Version specifiers

| Form | Meaning |
|---|---|
| `requests==2.32.3` | exactly this |
| `requests>=2.32` | this or newer |
| `requests~=2.32.0` | `>=2.32.0, <2.33.0` — compatible patch releases |
| `requests` | anything (avoid in real projects) |

**Rule of thumb:** a *library* declares loose bounds, an *application* pins strictly. The latter
is what lockfiles are for.

### `requirements.txt` vs a lockfile

```bash
python -m pip freeze > requirements.txt
```

`freeze` writes the **full, transitive** dependency tree with exact versions. It is a
poor man's lockfile: reproducible, but it does not distinguish what *you* asked for from what
came along as a dependency. Hence the two-file convention:

- `requirements.in` — what **you** require (`pandas>=2.2`)
- `requirements.txt` — generated, fully pinned (`pip-compile` or `uv pip compile`)

## `uv` — the modern tool

`uv` (written in Rust, by Astral) replaces `pip`, `venv`, `pyenv`, `pip-tools` and `virtualenv`
with a single binary, an order of magnitude faster. In 2026 it is the default choice for a new
project — which does not make `pip`/`venv` optional knowledge, because 90% of existing projects
still use them.

```bash
uv init hello-tool          # new project with a pyproject.toml
uv venv                     # virtual environment (.venv)
uv add pandas               # add dependency + install + update lockfile
uv add --dev pytest ruff    # development dependency
uv sync                     # recreate the exact environment from the lockfile
uv run pytest               # run inside the project environment, no activation needed
uv python install 3.12      # install an interpreter version
```

`uv` writes `uv.lock` — **commit this**; it is your reproducibility guarantee (the equivalent of
`package-lock.json`).

## Which one should you use?

| Situation | Tool |
|---|---|
| New project, free choice | `uv` |
| Existing project with `requirements.txt` | `venv` + `pip` |
| Just trying out a CLI tool | `uvx ruff check .` (runs without installing) |
| Data-science stack with conda packages | `conda` / `mamba` (a different universe; not covered here) |

## Typical failures and their real cause

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'pandas'` right after installing it | installed into a different interpreter | use `python -m pip install`, check `sys.executable` |
| Red squiggles in VS Code, works in the terminal | the IDE uses another interpreter | `Python: Select Interpreter` → the `.venv` |
| `pip install` says "Permission denied" | you are installing into the system Python | create a venv (never `sudo pip install`) |
| Works on a colleague's machine, not on yours | versions not pinned | lockfile or `pip freeze` |

## Check yourself

1. Why is `pip install` not enough on its own — why do you need a virtual environment?
2. What exactly does the `activate` script change?
3. What is the difference between `requirements.in` and `requirements.txt`?
4. Why do we not commit `.venv` but do commit `uv.lock`?
5. What does `pip install -e .` mean and when do you use it?
