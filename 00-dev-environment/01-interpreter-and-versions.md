# 01 — The interpreter, versions, installation

## What "Python" actually means

Three different things share the name, and mixing them up causes confusion later:

1. **The language** — syntax and semantics, described by the Language Reference.
2. **The implementation** — the program that runs it. The reference implementation is
   **CPython** (written in C; this is what 99% of people download from python.org). Others exist:
   *PyPy* (with a JIT, often 5–10× faster), *Jython* (on the JVM), *IronPython* (on .NET),
   *MicroPython* (microcontrollers), *GraalPy*. Unless stated otherwise, we always mean CPython.
3. **The standard library** — the modules shipped with the language (`json`, `pathlib`,
   `datetime`, …). "Batteries included" is one of Python's historical strengths.

## Compiled or interpreted?

The usual answer — "interpreted" — is inaccurate. What actually happens:

```
source code (.py)
   |  compilation (CPython does this automatically)
bytecode (.pyc, stored in __pycache__)
   |  execution
CPython virtual machine (a big evaluation loop)
```

So there **is** a compilation step; it just targets bytecode rather than machine code, and it
runs implicitly before execution, caching the result in `__pycache__/`. The model closely
resembles Java's `.class` files, with two important differences:

- compilation is **implicit** (there is no separate `javac` step), and
- the CPython VM has **no JIT** (3.13 ships an experimental one, off by default), so pure-Python
  compute-heavy code is an order of magnitude slower than the Java equivalent. NumPy and pandas
  solve this later by pushing the heavy work down into C/Rust.

See what your code actually compiles to:

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
```

```
  2           0 LOAD_FAST                0 (a)
              2 LOAD_FAST                1 (b)
              4 BINARY_OP                0 (+)
              8 RETURN_VALUE
```

This is not a party trick: `dis` is one of the fastest ways to decide which of two
implementations does less work.

## The GIL — expect this at a junior interview

CPython has a **Global Interpreter Lock**: only **one thread at a time** can execute Python
bytecode inside a single process. Consequences:

- **CPU-bound** work is **not** sped up by `threading`, no matter how many cores you have.
  Use `multiprocessing` (separate processes) or libraries that release the GIL in C code (NumPy).
- **I/O-bound** work (network, files, database) **is** sped up by `threading`, because the GIL
  is released while waiting for I/O.
- Since 3.13 there is an experimental *free-threaded* build without the GIL (PEP 703), but in
  2026 it is not yet the default for production work.

Details in [04-building-applications/04-concurrency.md](../04-building-applications/04-concurrency.md).

## Versions and compatibility

Python versions are `3.MINOR.PATCH`. **One minor release per year** (around October), and each
minor release is supported for **five years**.

| Version | What it brought that matters today |
|---|---|
| 3.6 | f-strings |
| 3.7 | `dataclasses`; `dict` ordering became a language guarantee |
| 3.8 | walrus operator (`:=`), positional-only parameters |
| 3.9 | `dict` union (`\|`), built-in generics (`list[int]`) |
| 3.10 | `match` statement, `X \| Y` type unions, much better error messages |
| 3.11 | ~25% faster, exception groups, `tomllib` |
| 3.12 | new generic syntax, even better error messages |
| 3.13 | rewritten REPL, experimental free-threading and JIT |

**What this means in practice:** if a project declares `requires-python = ">=3.9"`, you cannot
use `match`. Always check which version you are targeting — introducing the newest syntax into
an older codebase is a classic junior mistake.

**This course requires 3.12+.**

## Installation

### Windows

Use the official installer from [python.org/downloads](https://www.python.org/downloads/).
Two things to do differently from clicking Next-Next-Finish:

1. Tick **"Add python.exe to PATH"**.
2. Keep the **`py` launcher** (ticked by default).

> Do **not** use the Microsoft Store build: its sandboxed filesystem behaves surprisingly at
> times. The pre-installed `python.exe` stub in Windows is not Python at all, just a redirect
> to the Store.

The `py` launcher is Windows-specific but very useful:

```powershell
py --list          # which Python versions are installed
py -3.12 -V        # run a specific version
py -m venv .venv   # run a module (more on this below)
```

### macOS

The system Python is outdated and used by the OS itself — **do not touch it**.
Use Homebrew (`brew install python@3.12`) or `uv` (next chapter).

### Linux

Distribution packages (`apt install python3.12 python3.12-venv`) or `uv`. Again, never
overwrite the system Python: the package manager depends on it.

### Several versions on one machine

A realistic situation: one project targets 3.10, another 3.13.

- **Windows:** the `py -3.10` / `py -3.13` launcher handles it.
- **Anywhere:** `uv python install 3.10 3.13` — `uv` manages interpreters too.
- **Unix, classic:** `pyenv`.

## The `python -m` form

You will see this constantly:

```bash
python -m pip install requests     # instead of: pip install requests
python -m venv .venv
python -m pytest
python -m http.server 8000
```

`-m` means: *"run this module as a script, using **this** interpreter."*

This is not a style preference. If you type plain `pip`, the shell looks it up on `PATH` and
may well find **a different Python's `pip`** than the one you intend to run your code with.
This is the source of the single most common beginner frustration: *"but I installed it, why
can't it find it?"*

**Rule: always `python -m pip`, never bare `pip`.**

## Check yourself

1. What is the difference between the Python language and CPython?
2. Where is bytecode stored, and when is it regenerated?
3. Why does `threading` not speed up CPU-bound code? When does it help?
4. What exactly does `python -m pip` do, and why is it better than `pip`?
5. How do you find out whether you are allowed to use a `match` statement in a given project?
