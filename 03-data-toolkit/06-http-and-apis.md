# 06 — HTTP, REST APIs, `requests`

You know HTTP and REST. This chapter is about doing it in Python without writing the three bugs
everyone writes first: no timeout, no error check, and secrets in the source.

## `requests` basics

```python
import requests

response = requests.get("https://api.example.com/rates", timeout=10)

response.status_code        # 200
response.ok                 # True for 2xx
response.text               # body as str
response.json()             # parsed JSON (raises if the body is not JSON)
response.headers["Content-Type"]
response.elapsed
```

### Always pass a timeout

```python
requests.get(url)                 # can hang FOREVER - there is no default timeout
requests.get(url, timeout=10)     # correct
requests.get(url, timeout=(3, 27))   # (connect, read)
```

This is the single most common production bug in Python HTTP code: one unresponsive server
blocks a worker until someone restarts the process.

### Always check the status

```python
response = requests.get(url, timeout=10)
response.raise_for_status()        # raises HTTPError for 4xx/5xx
data = response.json()
```

Without `raise_for_status()`, a 500 response with an HTML error page reaches `response.json()`
and fails with a confusing `JSONDecodeError` far from the real cause.

### Query parameters, headers, bodies

```python
response = requests.get(
    "https://api.example.com/transactions",
    params={"from": "2024-01-01", "limit": 100},     # correctly URL-encoded for you
    headers={"Accept": "application/json", "User-Agent": "course-demo/1.0"},
    timeout=10,
)

response = requests.post(url, json={"amount": 100, "currency": "EUR"}, timeout=10)  # JSON body
response = requests.post(url, data={"field": "value"}, timeout=10)                  # form body
response = requests.post(url, files={"report": open("r.csv", "rb")}, timeout=30)    # upload
```

Never build a query string by concatenation — `params=` handles escaping, spaces and unicode.

## Sessions

```python
with requests.Session() as session:
    session.headers.update({"Authorization": f"Bearer {token}"})
    for page in range(1, 10):
        response = session.get(url, params={"page": page}, timeout=10)
        ...
```

A `Session` reuses the TCP connection (much faster for many requests) and keeps headers and
cookies. Use one whenever you make more than a couple of calls.

## Authentication and secrets

```python
import os
from dotenv import load_dotenv

load_dotenv()                                  # reads .env into os.environ, for development
API_KEY = os.environ["API_KEY"]                # KeyError at startup if missing - good
BASE_URL = os.getenv("BASE_URL", "https://api.example.com")
```

```
# .env - NEVER committed; .env.example is committed with empty values
API_KEY=secret-value-here
```

Rules:

1. No secret is ever hard-coded, and none is ever committed.
2. Use `os.environ["X"]` for required settings — failing at startup beats failing at 3 a.m.
3. Never log a token or a full `Authorization` header.

Passing credentials:

```python
session.headers["Authorization"] = f"Bearer {API_KEY}"        # most common
requests.get(url, auth=("user", "password"), timeout=10)      # HTTP basic
requests.get(url, params={"api_key": API_KEY}, timeout=10)    # in the query string (weakest)
```

## Error handling

```python
import logging
import requests

logger = logging.getLogger(__name__)


def fetch_rates(url: str, timeout: float = 10) -> dict[str, float] | None:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        logger.warning("timed out after %ss: %s", timeout, url)
    except requests.HTTPError as exc:
        logger.error("HTTP %s from %s", exc.response.status_code, url)
    except requests.ConnectionError:
        logger.error("cannot reach %s", url)
    except ValueError:                       # json() on a non-JSON body
        logger.error("invalid JSON from %s", url)
    return None
```

The exception hierarchy: everything derives from `requests.RequestException`, with
`Timeout`, `ConnectionError`, `HTTPError` and `TooManyRedirects` beneath it. Catch the specific
ones; catch the base class as a last resort.

## Retries and backoff

Transient failures are normal. Retry them — with an increasing delay, and only for retriable
status codes.

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry = Retry(
    total=5,
    backoff_factor=0.5,                       # 0.5s, 1s, 2s, 4s...
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "HEAD"],          # never blindly retry a POST
)

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry))
```

Do not retry 4xx errors other than 429: a 404 will still be a 404 on the fifth attempt. And
respect `Retry-After` when the server sends it.

## Pagination

```python
def fetch_all(session: requests.Session, url: str) -> list[dict[str, object]]:
    """Follow the pages until the API stops giving us data."""
    items: list[dict[str, object]] = []
    page = 1

    while True:
        response = session.get(url, params={"page": page, "per_page": 100}, timeout=10)
        response.raise_for_status()
        batch = response.json()["items"]

        if not batch:
            break

        items.extend(batch)
        page += 1

        if page > 1000:                       # a guard against an infinite loop
            raise RuntimeError("suspiciously many pages")

    return items
```

Cursor-based APIs give you a `next` link instead; follow it until it is absent. Either way,
**always** have a stop condition that does not depend on the server behaving.

A generator version streams instead of accumulating, which matters for large exports:

```python
def iter_items(session, url) -> Iterator[dict[str, object]]:
    page = 1
    while True:
        batch = session.get(url, params={"page": page}, timeout=10).json()["items"]
        if not batch:
            return
        yield from batch
        page += 1
```

## From API to DataFrame

```python
import pandas as pd

response = requests.get("https://api.example.com/transactions", timeout=10)
response.raise_for_status()

df = pd.DataFrame(response.json()["items"])
df = pd.json_normalize(response.json()["items"], sep="_")     # flattens nested objects
```

`pd.json_normalize` turns `{"user": {"name": "Anna"}}` into a `user_name` column — the fastest
way from a JSON API to a table.

## Downloading a file

```python
with requests.get(url, stream=True, timeout=30) as response:
    response.raise_for_status()
    with open("export.csv", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
```

`stream=True` avoids loading a 2 GB file into memory.

## Testing code that calls an API

Never hit the real network in a unit test. Inject the session, or patch it:

```python
from unittest.mock import Mock

def test_fetch_rates_parses_response() -> None:
    session = Mock()
    session.get.return_value.json.return_value = {"EUR": 1.0, "HUF": 389.5}
    session.get.return_value.raise_for_status.return_value = None

    assert fetch_rates(session, "https://x") == {"EUR": 1.0, "HUF": 389.5}
```

The library `responses` (or `respx` for httpx) mocks at the HTTP layer, which is closer to
reality and reads better for anything more than one call.

## `httpx` — the modern alternative

Same API, plus HTTP/2 and async:

```python
import httpx

with httpx.Client(timeout=10) as client:
    response = client.get(url)

async with httpx.AsyncClient(timeout=10) as client:
    response = await client.get(url)            # see module 04 on asyncio
```

For new code that needs concurrency, prefer `httpx`. For everything else, `requests` is fine
and is what you will find in existing projects.

## Etiquette

- Send a meaningful `User-Agent`.
- Respect rate limits; back off on 429 instead of hammering.
- Cache what does not change (a file, a database, `functools.cache` for a process lifetime).
- Read the terms of service before scraping anything, and prefer the documented API.

## Check yourself

1. What happens if you omit `timeout=`?
2. Why call `raise_for_status()` before `json()`?
3. Why build query strings with `params=` instead of an f-string?
4. When is a `Session` worth it?
5. Which status codes are worth retrying, and which are not?
6. How do you keep an API key out of your repository?
