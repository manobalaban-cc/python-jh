# Junior Python developer — self-assessment

Go through it honestly. Anything you cannot **explain out loud** is not yet knowledge you can
use in an interview or a code review. The bracketed references point at the chapter that covers it.

## Language and runtime

- [ ] I can explain what happens when Python runs a `.py` file (compilation to bytecode, the VM). [00/01]
- [ ] I can explain the GIL and what it does and does not prevent. [00/01, 04/04]
- [ ] I can explain what `b = a` does when `a` is a list, and when that surprises people. [01/01]
- [ ] I know the difference between `is` and `==` and when each is correct. [01/01]
- [ ] I can list the mutable and immutable built-in types and say why it matters for dict keys. [01/01]
- [ ] I know the difference between a shallow and a deep copy. [01/01]
- [ ] I can explain why `-7 // 2 == -4`. [01/02]
- [ ] I know why `float` is wrong for money and what replaces it. [01/02]
- [ ] I can explain truthiness and the bug it causes when `0` is a valid value. [01/02]
- [ ] I know when to use `list`, `tuple`, `dict`, `set`, `deque`, and the cost of their operations. [01/04]
- [ ] I can explain the difference between an iterable and an iterator. [01/05]
- [ ] I know what a generator is, when it runs, and why it saves memory. [01/05]
- [ ] I can explain the mutable-default-argument trap and its fix. [01/06]
- [ ] I know what LEGB is and why `counter += 1` can raise `UnboundLocalError`. [01/06]
- [ ] I can explain the late-binding closure trap. [01/06]
- [ ] I know what EAFP means and why Python prefers it. [01/07]
- [ ] I can read a traceback and find where to start looking. [reference/error-messages]

## Object orientation

- [ ] I can explain why `self` is explicit. [02/01]
- [ ] I know why a mutable class attribute is a bug. [02/01]
- [ ] I know when to use a property instead of a getter. [02/01]
- [ ] I know the difference between `@classmethod` and `@staticmethod`. [02/01]
- [ ] I write `__repr__` on my classes and can say why. [02/02]
- [ ] I know what defining `__eq__` does to `__hash__`. [02/02]
- [ ] I can choose between `dict`, `NamedTuple`, `dataclass` and a Pydantic model, with reasons. [02/03, 04/02]
- [ ] I know what `frozen=True` buys me. [02/03]
- [ ] I can explain duck typing, and what `Protocol` adds to it. [02/04]
- [ ] I know when to use an ABC instead of a Protocol. [02/04]
- [ ] I prefer composition, and can say why it is especially cheap in Python. [02/04]

## Typing and tooling

- [ ] I know what annotations do at runtime (and which libraries are the exception). [02/05]
- [ ] I annotate parameters liberally and return types specifically. [02/05]
- [ ] I can run `mypy` and fix what it finds without reaching for `# type: ignore`. [02/05]
- [ ] I can set up a project from scratch: venv, `pyproject.toml`, `src/` layout, editable install. [00/02, 00/03]
- [ ] I can explain why `python -m pip` is safer than `pip`. [00/01]
- [ ] I know what `pip install -e .` does. [00/03]
- [ ] I can explain what `import` does and why my module is not found. [00/03]
- [ ] `ruff` and `mypy` run clean on my code before I open a PR. [00/04]
- [ ] I can debug with `breakpoint()` / the IDE debugger, not just `print`. [00/04]

## Standard library

- [ ] `pathlib` instead of string paths. [02/06]
- [ ] `datetime`: naive vs aware, and why I store UTC. [02/06]
- [ ] `logging` instead of `print`, configured once, in the entry point. [02/06, 04/01]
- [ ] `collections`: `Counter`, `defaultdict`, `deque`. [01/04]
- [ ] `json` and `csv`, with an explicit encoding and `newline=""`. [02/08]
- [ ] `re`, with raw strings and compiled patterns — and I know when *not* to use a regex. [02/06]
- [ ] I can find the right standard-library module before adding a dependency. [02/06]

## Testing

- [ ] I can write a `pytest` test, a parametrized test and a fixture. [02/09]
- [ ] I know what `tmp_path`, `monkeypatch`, `capsys` and `caplog` are for. [02/09]
- [ ] I can mock an external call, and I know what I should *not* mock. [02/09]
- [ ] I test error paths, not just the happy path. [02/09]
- [ ] I know why 100% coverage is not the goal. [02/09]

## Data

- [ ] I can explain why NumPy is faster than a list of numbers. [03/01]
- [ ] I know the difference between `loc` and `iloc`. [03/02]
- [ ] I know why `df[a > 1 and b < 2]` fails. [03/02]
- [ ] I never loop over DataFrame rows, and can say what to do instead. [03/02]
- [ ] I can load a messy CSV: encoding, separator, decimal comma, missing-value markers. [03/03]
- [ ] I can explain when filling missing values with `0` is wrong. [03/03]
- [ ] `groupby` + named aggregation, `transform`, `merge` with `validate`, `pivot`/`melt`. [03/04]
- [ ] I check row counts before and after a merge. [03/04]
- [ ] I can choose a chart type and justify it, and I know why dual axes are banned. [03/05]

## HTTP and applications

- [ ] Every outbound request has a timeout and a `raise_for_status()`. [03/06]
- [ ] I know which status codes are worth retrying. [03/06]
- [ ] No secret is ever in my source or my repository. [03/06, 04/01]
- [ ] I can build a CLI with `argparse`, exit codes, and stdout/stderr used correctly. [04/01]
- [ ] I can build a small FastAPI service with separate In/Out models. [04/02]
- [ ] I know when an endpoint must not be `async def`. [04/02, 04/04]
- [ ] I never build SQL with string formatting. [04/03]
- [ ] I can recognise and fix an N+1 query. [04/03]
- [ ] I can say whether threads, processes or async fits a given problem. [04/04]
- [ ] I can containerise an application and explain the layer order in the Dockerfile. [04/05]
- [ ] I measure before optimising, and I know which optimisations pay. [04/06]

## Working habits

- [ ] My commits are small and their messages say why.
- [ ] My README lets someone else run the project without asking me.
- [ ] I write down the decision I made and the alternative I rejected.
- [ ] When something breaks, I read the error before changing code.
- [ ] I can say "I do not know, but here is how I would find out" — and then do it.

## Typical junior interview questions from this material

1. What is the difference between a list and a tuple, and when does it matter?
2. What is the GIL? What does it stop you doing?
3. What is a decorator? Write one that measures execution time.
4. What is a generator and when would you use one?
5. What does `if __name__ == "__main__":` do?
6. What is the difference between `is` and `==`?
7. Why is `def f(x=[])` dangerous?
8. How would you handle an API that sometimes times out?
9. You have a 10 GB CSV and 8 GB of RAM. What do you do?
10. How do you test code that calls an external service?
11. What is the difference between `loc` and `iloc`?
12. Your import job produced numbers twice as large as expected. How do you investigate?
