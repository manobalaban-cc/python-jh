# 06 — Performance: measure, then optimise

> "Premature optimisation is the root of all evil" is quoted far more often than the rest of the
> sentence, which is about the 3% of code where optimisation *does* matter. The job is to find
> that 3% with a measurement rather than a guess.

## Timing

```python
import time

start = time.perf_counter()
result = do_work()
print(f"{time.perf_counter() - start:.3f}s")
```

Use `time.perf_counter()` (monotonic, high resolution), not `time.time()` (wall clock, can jump
backwards when the system clock is adjusted).

For small snippets, `timeit` runs them many times and reports the best:

```bash
python -m timeit -s "items = list(range(1000))" "sum(items)"
python -m timeit -s "items = list(range(1000))" "total = 0
for i in items: total += i"
```

```python
import timeit

timeit.timeit("'-'.join(str(n) for n in range(100))", number=10_000)
```

## Profiling — where is the time going?

```bash
python -m cProfile -s cumtime myscript.py | head -30
python -m cProfile -o profile.out myscript.py
```

```python
import cProfile
import pstats

with cProfile.Profile() as profiler:
    main()

stats = pstats.Stats(profiler).sort_stats("cumtime")
stats.print_stats(20)
```

Reading the output:

| Column | Meaning |
|---|---|
| `ncalls` | how many times it was called |
| `tottime` | time inside this function, excluding sub-calls |
| `cumtime` | time including everything it called |

Sort by `cumtime` to find *which part* of the program is slow; by `tottime` to find *which
function* is doing the work. A function with a huge `ncalls` and a tiny `tottime` is usually a
loop that should be vectorised or hoisted.

Line-by-line, when you have narrowed it down:

```bash
pip install line_profiler
kernprof -l -v myscript.py        # decorate the function with @profile
```

Third-party profilers worth knowing: `py-spy` (attaches to a *running* process — invaluable in
production), `scalene` (CPU plus memory), `snakeviz` (a flame-graph view of `profile.out`).

## Memory

```python
import sys
sys.getsizeof([1, 2, 3])          # shallow size of one object

import tracemalloc
tracemalloc.start()
run_job()
current, peak = tracemalloc.get_traced_memory()
print(f"current {current / 1e6:.1f} MB, peak {peak / 1e6:.1f} MB")
```

For pandas:

```python
df.memory_usage(deep=True).sum() / 1e6
df.info(memory_usage="deep")
```

## The wins that actually pay, in order

1. **A better algorithm or data structure.** `x in list` → `x in set` turns `O(n)` into `O(1)`;
   nothing else you do will match that.
2. **Do less work.** Read fewer columns, filter earlier, cache a repeated call, avoid recomputing
   inside a loop.
3. **Vectorise.** In pandas/NumPy, replacing a row loop with a column operation is routinely a
   100× change.
4. **Batch I/O.** One query returning 1,000 rows beats 1,000 queries. `executemany` beats a loop
   of `execute`. One HTTP call with 100 ids beats 100 calls.
5. **Parallelise** — threads for I/O, processes for CPU (see [04-concurrency.md](04-concurrency.md)).
6. **Micro-optimisations** (local variable lookups, `__slots__`, comprehension instead of
   `append`) — real, but small. Only after the five above.
7. **A different runtime**: PyPy, or moving the hot loop into C/Rust (Cython, `numba`, PyO3).
   Rare in application work.

## Common Python-specific slowness

```python
# String concatenation in a loop: O(n^2)
result = ""
for line in lines:
    result += line              # -> "".join(lines)

# Repeated attribute or global lookup in a hot loop
for item in items:
    self.repository.save(item)  # -> save = self.repository.save  before the loop

# Rebuilding a constant inside the loop
for row in rows:
    valid = set(load_currencies())   # -> hoist it out

# Membership testing against a list
for row in rows:
    if row.currency in currency_list:    # -> convert to a set once

# Row loops in pandas
for _, row in df.iterrows():             # -> vectorised column operations
```

## Caching

```python
from functools import cache, lru_cache


@cache
def exchange_rate(day: date, currency: str) -> Decimal:
    ...                                  # an expensive, pure lookup
```

Cache only **pure** functions (same input, same output), watch the memory (`lru_cache(maxsize=…)`
bounds it), and remember that the cache lives for the life of the process — it is not a
distributed cache, and it will not see a change in the underlying data.

## Before you optimise anything

1. Is it actually slow? Measure, with a realistic input size.
2. Does it matter? A report that runs nightly and takes 40 seconds does not need your attention.
3. What is the target? "Fast enough" needs a number.
4. Write a benchmark you can re-run, so you can prove the change helped.
5. Keep the tests green — a fast wrong answer is worthless.

## Check yourself

1. Why `time.perf_counter()` rather than `time.time()`?
2. What is the difference between `tottime` and `cumtime` in a profile?
3. Which optimisation usually gives the biggest win, and why?
4. Why is `+=` on strings in a loop quadratic?
5. When is `@cache` unsafe?
6. What should you do before starting to optimise?
