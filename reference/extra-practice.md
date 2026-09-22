# Extra practice and further reading

The course exercises come first — this is for the evening, the commute and the weeks after the
course ends.

## Katas

[Codewars](https://www.codewars.com/) with Python selected. Skip the 8 kyu "return the opposite
number" level; you are past it. Start at **6 kyu** and use the kata to practise *idiom*, not
logic: solve it, then open the "Solutions" tab and compare yours against the most-upvoted
Python answers. That comparison is where the learning is.

A curated list, kept from the earlier version of this course, that exercises things this
material covers:

| Kata | What it drills |
|---|---|
| Find the odd int | `Counter`, XOR, `functools.reduce` |
| Split Strings | slicing, `zip`, `itertools` |
| Mumbling | `enumerate`, string building with `join` |
| Disemvowel Trolls | `str.translate`, comprehensions, sets |
| Categorize New Member | list of tuples, comprehension with a condition |
| Your order, please | `sorted` with a `key` function |
| Who likes it? | `match`/`len` dispatch, f-strings |
| Duplicate Encoder | `Counter`, `str.lower`, generator expressions |
| Moving Zeros To The End | stable sort with a `key`, list building |
| Valid Parentheses | a stack built from a list, early return |
| Human Readable Time | `divmod`, format specifiers |
| Where my anagrams at? | `sorted(word)` as a key, `defaultdict` |
| Rot13 | `str.maketrans`, `str.translate`, ASCII arithmetic |
| Highest and Lowest | `min`/`max` with `key`, splitting input |

Other sites worth the time:

- **[Exercism](https://exercism.org/tracks/python)** — the Python track has human mentoring and
  its exercises target idiom explicitly. Probably the best fit for this audience.
- **[Advent of Code](https://adventofcode.com/)** — parsing messy input, which is 80% of real work.
- **[LeetCode](https://leetcode.com/)** — only if you are preparing for an algorithm interview;
  it teaches little about Python itself.

## Books

| Book | For |
|---|---|
| *Fluent Python*, 2nd ed. (Ramalho) | **the** book for exactly this audience: experienced developers who want to write real Python. Read chapters 1–6 during the course. |
| *Effective Python*, 2nd ed. (Slatkin) | 125 short, specific items. Read one a day. |
| *Python Cookbook* (Beazley & Jones) | recipes you will actually reach for |
| *Architecture Patterns with Python* (Percival & Gregory) | repositories, services, dependency inversion — the natural next step after module 04 |
| *Python Testing with pytest* (Okken) | everything the testing chapter left out |
| *Python for Data Analysis*, 3rd ed. (McKinney) | pandas, by its author |
| *High Performance Python* (Gorelick & Ozsvald) | after module 04 chapter 06 |

## Documentation worth reading rather than searching

- [The Python Tutorial](https://docs.python.org/3/tutorial/) — skim it in an evening; you will
  find three things you did not know.
- [The Standard Library index](https://docs.python.org/3/library/) — skim the module list once,
  so you know what exists.
- [The Data Model](https://docs.python.org/3/reference/datamodel.html) — the dunder reference.
- [PEP 8](https://peps.python.org/pep-0008/), [PEP 20](https://peps.python.org/pep-0020/) (the Zen),
  [PEP 484](https://peps.python.org/pep-0484/) (type hints).
- [pandas user guide](https://pandas.pydata.org/docs/user_guide/) — the "10 minutes" page is a
  lie, but the rest is good.
- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) — genuinely one of the best
  framework tutorials in any language.

## Keeping up

- **Real Python** — reliable, deep articles.
- **Python Bytes** / **Talk Python** — podcasts, good for the commute.
- **[What's new in Python 3.x](https://docs.python.org/3/whatsnew/)** — read it once a year.
- The release notes of the libraries you depend on. Reading the pandas 3.0 notes is what stops
  you being the person who does not know copy-on-write changed.

## A habit worth building

Once a week, open a file you wrote a month ago and improve it. Not rewrite — improve: a clearer
name, a comprehension instead of a loop, a missing type annotation, a test for the case you were
not sure about. Half an hour a week of that beats any book.
