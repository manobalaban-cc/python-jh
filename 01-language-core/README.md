# 01 — Language core

This module does not teach you what a loop or a function is. It teaches you why these work
**differently** in Python from what you are used to, and what that means for the code you write.

| Chapter | Topic | What people from other languages get wrong |
|---|---|---|
| [01](01-object-model.md) | Object model, names, references, mutability | "assignment copies" — it does not |
| [02](02-types-and-strings.md) | Numbers, strings, `None`, conversions, formatting | `int` is not 32-bit; strings are immutable |
| [03](03-control-flow.md) | `if`, `for`, `while`, `match`, truthiness | there is no C-style `for`; `for...else` exists |
| [04](04-collections.md) | `list`, `tuple`, `dict`, `set`, costs of operations | when to use which, and why not always a list |
| [05](05-iteration-and-comprehensions.md) | Iterator protocol, comprehensions, generators | a comprehension is not "a shorter loop" |
| [06](06-functions.md) | Argument passing, defaults, `*args`, scope, closures | the mutable default trap |
| [07](07-exceptions.md) | Exceptions, EAFP, custom exceptions, `finally` | here, exceptions are not exceptional |
| [exercises/](exercises/) | Exercise sets verified with `pytest` | |

## By the end of this module

- You can explain what happens in memory on `b = a`, and when that surprises people.
- You know when to reach for `list`, `tuple`, `dict` or `set`, and can talk about the cost of
  the operations.
- You write comprehensions and generator expressions instead of loops — where they are genuinely better.
- You never write `def f(items=[])`, and you can explain why.
- You handle errors the Python way (EAFP) instead of with Java's null-check reflex.

## How to practise

Each chapter has a task file and a matching test file in `exercises/`. The workflow:

```bash
cd 01-language-core/exercises
python -m pytest tests/test_01_object_model.py -v     # red
# ... implement in tasks/ ...
python -m pytest tests/test_01_object_model.py -v     # green
```

Solutions are in `exercises/solutions/` — open them only after you have tried.

## Required reading alongside this module

- [The Zen of Python](https://peps.python.org/pep-0020/) — run `import this`. Not a joke: it
  states the design principles of the language, and people will cite it in code review.
- [PEP 8](https://peps.python.org/pep-0008/) — style. You do not need to memorise it, `ruff` knows it.
- [reference/from-java-csharp.md](../reference/from-java-csharp.md) — the migration cheat sheet.
