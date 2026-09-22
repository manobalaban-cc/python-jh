# 04 — Concurrency: threads, processes, asyncio

## The decision, first

| Your work is… | Use | Why |
|---|---|---|
| I/O-bound, a handful of tasks | `concurrent.futures.ThreadPoolExecutor` | simplest thing that works; the GIL is released during I/O |
| I/O-bound, hundreds or thousands of tasks | `asyncio` | one thread, no per-task stack, scales to thousands of sockets |
| CPU-bound | `ProcessPoolExecutor` / `multiprocessing` | separate processes, separate GILs, real parallelism |
| CPU-bound numeric work | NumPy / pandas / Polars | the loop already runs in C, often multi-threaded |
| Long-running background jobs | a task queue (Celery, RQ, Dramatiq) | survives restarts, retries, observability |

Getting this wrong is the classic junior mistake: adding threads to a CPU-bound job and
measuring no improvement at all.

## Why: the GIL again

In CPython only one thread executes Python bytecode at a time. The lock is released:

- while waiting on I/O (network, disk, database);
- inside C extensions that explicitly release it (NumPy does this for large operations).

So threads help when your program is *waiting*, and not when it is *computing*.

```python
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def cpu_work(n: int) -> int:
    return sum(i * i for i in range(n))


def io_work(url: str) -> int:
    return len(requests.get(url, timeout=10).content)
```

`cpu_work` in four threads: no faster than sequential. In four processes: roughly four times
faster. `io_work` in four threads: roughly four times faster.

## `concurrent.futures` — the simple API

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

urls = ["https://example.com/1", "https://example.com/2", ...]

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(fetch, urls))          # ordered, raises on the first failure

with ThreadPoolExecutor(max_workers=8) as pool:
    futures = {pool.submit(fetch, url): url for url in urls}
    for future in as_completed(futures):           # as they finish
        url = futures[future]
        try:
            data = future.result()
        except Exception:
            logger.exception("failed: %s", url)
```

Swap in `ProcessPoolExecutor` and the same code runs in processes — with two caveats:
everything passed and returned must be **picklable**, and there is real overhead per task, so
batch small jobs together.

```python
with ProcessPoolExecutor() as pool:                # defaults to os.cpu_count()
    results = list(pool.map(cpu_work, chunks, chunksize=10))
```

On Windows and macOS, child processes **re-import your module**, so the entry point must be
guarded:

```python
if __name__ == "__main__":
    main()
```

Without it, a `ProcessPoolExecutor` spawns children that spawn children.

## Threads and shared state

```python
import threading

lock = threading.Lock()
counter = 0


def increment() -> None:
    global counter
    with lock:                    # the critical section
        counter += 1              # not atomic: read, add, write
```

Everything you know about race conditions applies. Prefer designs that avoid shared mutable
state entirely: give each worker its own data and combine the results at the end — for example
with `queue.Queue`, which is thread-safe by design.

## `asyncio`

Cooperative multitasking in a single thread: a coroutine runs until it `await`s, then yields
control to the event loop.

```python
import asyncio
import httpx


async def fetch(client: httpx.AsyncClient, url: str) -> int:
    response = await client.get(url, timeout=10)
    return len(response.content)


async def main() -> None:
    async with httpx.AsyncClient() as client:
        # gather runs them concurrently
        sizes = await asyncio.gather(*(fetch(client, url) for url in urls))
        print(sum(sizes))


asyncio.run(main())
```

The modern form, with proper error handling (3.11+):

```python
async def main() -> None:
    results: list[int] = []
    async with asyncio.TaskGroup() as group:       # cancels the rest if one fails
        tasks = [group.create_task(fetch(client, url)) for url in urls]
    results = [task.result() for task in tasks]
```

Useful pieces:

```python
await asyncio.sleep(1)                             # never time.sleep in async code
async with asyncio.timeout(5):                     # 3.11+
    await slow_operation()
semaphore = asyncio.Semaphore(10)                  # limit concurrency
async with semaphore:
    await fetch(...)
```

### The rules that actually matter

1. **One blocking call poisons the loop.** `time.sleep`, `requests.get`, a synchronous database
   driver or a heavy computation inside a coroutine stops *everything*. Offload it:
   `await asyncio.to_thread(blocking_function, arg)`.
2. **Async is contagious.** Only a coroutine can `await`, so an async call at the bottom pulls
   `async def` all the way up the call stack.
3. **You need async libraries**: `httpx`/`aiohttp` instead of `requests`, `asyncpg` or an async
   SQLAlchemy engine instead of the synchronous one.
4. **Async is not faster for CPU work.** It is a concurrency model, not parallelism.
5. Calling a coroutine without awaiting it does nothing and warns — `RuntimeWarning:
   coroutine ... was never awaited`.

### When is it worth it?

For a handful of parallel HTTP calls, a thread pool is simpler and just as fast. Async pays off
at scale (hundreds or thousands of simultaneous connections), and in frameworks built around it
— FastAPI, aiohttp, message consumers. Do not convert a codebase to async without a measured
reason.

## A worked comparison

```python
import time
from concurrent.futures import ThreadPoolExecutor

import requests

URLS = ["https://httpbin.org/delay/1"] * 10


def sequential() -> None:
    start = time.perf_counter()
    for url in URLS:
        requests.get(url, timeout=30)
    print(f"sequential: {time.perf_counter() - start:.1f}s")      # ~10s


def threaded() -> None:
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(lambda u: requests.get(u, timeout=30), URLS))
    print(f"threaded:   {time.perf_counter() - start:.1f}s")      # ~1s
```

Ten requests that each wait one second take ten seconds in sequence and about one second in
parallel, because the waiting overlaps. Nothing about the GIL prevents that.

## Check yourself

1. Why does `threading` not speed up CPU-bound code?
2. When is `ProcessPoolExecutor` the right tool, and what must its arguments satisfy?
3. Why does a `ProcessPoolExecutor` script need `if __name__ == "__main__":`?
4. What happens if you call `requests.get()` inside an `async def`?
5. What does `asyncio.gather` do, and what does `TaskGroup` add?
6. When is a task queue the right answer instead of any of these?
