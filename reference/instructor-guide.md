# Instructor guide

## The audience

Graduates of a one-year intensive programming course who have never written Python. They know
OOP, Git, SQL, HTTP, testing and clean code. They do **not** know Python's syntax, its idioms,
its ecosystem or its tooling.

The two failure modes to avoid:

- **Teaching programming again.** They will disengage in an hour. Never explain what a loop is;
  explain why Python has no C-style `for`.
- **Assuming Python translates.** They will write Java in Python for the first two weeks. The
  material fights this deliberately — every chapter has a "what you will get wrong" angle.

## Six-week schedule

| Week | Self-study | Contact sessions | Deliverable |
|---|---|---|---|
| 0 (2 days) | Module 00 | 1 × 3h: environment set up together, live | Working project skeleton with CI |
| 1 | Module 01 | 2 × 3h: live coding, exercise review | Language-core exercises green |
| 2 | Module 02 | 2 × 3h: design discussion, code review | `txlib` project |
| 3 | Module 03 | 2 × 3h: pandas live, chart critique | Pandas exercises + the small analysis |
| 4 | Module 04 | 2 × 3h: API design, containers | Project 3 milestones 1–3 |
| 5 | Projects 1–2 | 1 × 3h: code review workshop | Projects 1 and 2 |
| 6 | Projects 3–4 | 1 × 3h + presentations | Capstone + a 20-minute presentation |

Adjustments that work:

- **Four weeks** (intensive): merge weeks 5–6 into project work alongside modules 03–04, and
  drop project 2 or 3.
- **Eight weeks** (part-time): one module per week, projects in weeks 7–8.
- **Self-paced**: the material is written to be readable alone; only the review sessions and
  the presentation need a group.

## Contact-session formats that work

**1. Live coding with deliberate mistakes (45 min).** Solve an exercise in front of them and
make the classic errors on purpose: mutable default, `iterrows`, a bare `except`. Let them catch
you. They remember the ones they spotted.

**2. Code review circle (60 min).** Two participants show the same exercise on screen. The group
reviews against the checklist in [junior-checklist.md](junior-checklist.md). The point is to
practise *receiving* review as much as giving it.

**3. "Translate this" (30 min).** Give them 20 lines of working Java/C#. They port it to Python,
then the group ranks the ports from most to least Pythonic.

**4. Debugging clinic (45 min).** Prepare five broken snippets, one per common error class
(`UnboundLocalError`, a late-binding closure, a shared mutable default, chained assignment in
pandas, a swallowed exception). Time-box each to five minutes.

**5. Reading the standard library (30 min).** Open the source of `dataclasses` or
`contextlib` together. It demystifies the language and teaches them that the answer is usually
readable.

## What to grade, and how hard

Weighting that matches what employers care about:

| | Weight |
|---|---|
| Works as specified | 30% |
| Design and structure | 25% |
| Idiomatic Python | 20% |
| Tests | 15% |
| Documentation and craft | 10% |

Automatic fail, regardless of the rest:

- a secret committed to the repository;
- SQL built by string formatting;
- tests that do not actually assert anything;
- a README that does not let you run the project.

## Common sticking points, and what fixes them

| Symptom | What is really going on | Intervention |
|---|---|---|
| Getters and setters everywhere | Java reflex | show `@property`; make them delete the getters and watch nothing break |
| `for i in range(len(x))` everywhere | C reflex | one exercise where they may not use `range` at all |
| Every function returns `None` and prints | script habit | make them test the function; it forces a return value |
| Fear of exceptions, null checks everywhere | checked-exception habit | the EAFP chapter, then a review pass deleting defensive code |
| `ModuleNotFoundError` chaos in week 1 | virtual environments not understood | 20 minutes on `sys.executable` and `sys.path`; this always pays off |
| pandas by trial and error | no mental model | make them state the shape and dtypes before and after each step |
| "it works but I do not know why" | copied from an LLM or Stack Overflow | ask them to explain it line by line; if they cannot, it goes back |

## On AI assistants

They will use them; pretending otherwise makes the training less realistic, not more rigorous.
What the material assumes instead:

- Generated code is **reviewed**, not pasted. The reviewer is the participant, and they are
  accountable for every line.
- In the presentation they must explain any line they are asked about. That is the real check.
- Exercises with hidden traps (mutable defaults, late binding, chained assignment) are the ones
  where naive generated code is subtly wrong — use those for discussion.

## Preparing the environment

Before day one, verify on the exact machines they will use:

- [ ] Python 3.12+ installs and `py --list` / `python3 -V` works
- [ ] Corporate proxy or firewall does not block PyPI (a classic day-one blocker)
- [ ] VS Code plus the Python, Pylance and Ruff extensions
- [ ] Git is configured, and they can push to the course organisation
- [ ] Docker is available for module 04 (or plan a hosted alternative)

## Where the material came from

This course replaces a Jupyter-based introduction written for finance professionals with no
programming background. Reused: the pandas and visualisation topics, and all the datasets in
[`../data/`](../data/), several of which are usefully messy. Removed: everything that teaches
programming itself, the notebook workflow, and the Bloomberg BQuant specifics.

The old material is still worth keeping for reference if you ever run the beginner version; it
lives in the original repository, where `pandas/` and `python_pandas/` are byte-identical copies
of the root — use the root.
