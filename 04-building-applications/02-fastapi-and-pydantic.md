# 02 — Pydantic and FastAPI

## Pydantic: validation from type annotations

A dataclass describes a shape. A Pydantic model **enforces** it at runtime — which is exactly
what you need at a trust boundary: request bodies, config files, external API responses.

```python
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class TransactionIn(BaseModel):
    timestamp: datetime
    amount: Decimal = Field(gt=0, description="Transaction amount, must be positive")
    currency: str = Field(min_length=3, max_length=3)
    recipient: str = Field(min_length=1, max_length=100)
    note: str = ""

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        value = value.upper()
        if value not in {"EUR", "USD", "GBP", "JPY", "CAD"}:
            raise ValueError(f"unsupported currency: {value}")
        return value
```

```python
tx = TransactionIn(
    timestamp="2024-05-01T10:00:00",     # parsed from a string into a datetime
    amount="250.50",                     # parsed into Decimal
    currency="eur",                      # normalised by the validator
    recipient="Amazon",
)

tx.model_dump()          # -> dict
tx.model_dump_json()     # -> JSON string
TransactionIn.model_validate(raw_dict)          # from a dict
TransactionIn.model_validate_json(raw_json)     # from JSON text
```

On invalid input it raises `ValidationError` with a precise, machine-readable report:

```python
try:
    TransactionIn(timestamp="yesterday", amount=-5, currency="EURO", recipient="")
except ValidationError as exc:
    print(exc.errors())
    # [{'loc': ('timestamp',), 'msg': 'Input should be a valid datetime', ...},
    #  {'loc': ('amount',), 'msg': 'Input should be greater than 0', ...}, ...]
```

Nesting and collections work as expected:

```python
class Batch(BaseModel):
    source: str
    imported_at: datetime
    transactions: list[TransactionIn]
```

### dataclass or Pydantic model?

| | `@dataclass` | Pydantic `BaseModel` |
|---|---|---|
| Validation | none | full, at construction |
| Coercion | none | strings to `int`/`datetime`/`Decimal` |
| Speed | faster | fast enough (v2 core is Rust) |
| Dependency | standard library | third party |
| Use for | internal domain objects | API boundaries, config, external data |

Rule: **validate at the edges, use plain objects inside.** Do not turn every internal type into
a Pydantic model; you pay validation cost for data you already trust.

## FastAPI

```python
from fastapi import FastAPI, HTTPException, Query, status

app = FastAPI(title="Transactions API", version="1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/transactions", response_model=list[TransactionOut])
def list_transactions(
    currency: str | None = None,
    min_amount: float = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
) -> list[Transaction]:
    return repository.find(currency=currency, min_amount=min_amount, limit=limit)


@app.get("/transactions/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int) -> Transaction:
    transaction = repository.get(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    return transaction


@app.post("/transactions", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionIn) -> Transaction:
    return repository.add(payload)
```

What the framework derives from those annotations:

- **path parameters** (`transaction_id: int`) — parsed and validated, 422 on a bad value;
- **query parameters** (anything not in the path) with constraints from `Query(...)`;
- **the request body** (any Pydantic model parameter) — parsed, validated, 422 with details;
- **the response** — filtered and serialised through `response_model`;
- **OpenAPI documentation**, live at `/docs` and `/redoc`.

Running it:

```bash
uvicorn myservice.api:app --reload          # development
uvicorn myservice.api:app --host 0.0.0.0 --port 8000 --workers 4   # production-ish
```

### Separate input and output models

```python
class TransactionIn(BaseModel):      # what the client may send
    amount: Decimal
    currency: str
    recipient: str


class TransactionOut(BaseModel):     # what we return
    id: int
    amount: Decimal
    currency: str
    recipient: str
    created_at: datetime
```

Never expose your database model directly. The input model prevents a client from setting `id`
or `created_at`; the output model prevents an internal field (a password hash, an internal
note) from leaking the day someone adds it to the table.

### Dependency injection

```python
from typing import Annotated
from fastapi import Depends


def get_repository() -> Iterator[Repository]:
    with SessionLocal() as session:
        yield SqlRepository(session)


RepositoryDep = Annotated[Repository, Depends(get_repository)]


@app.get("/transactions")
def list_transactions(repository: RepositoryDep) -> list[TransactionOut]:
    return repository.all()
```

Dependencies are how FastAPI gives you a database session, the current user, or a settings
object — and, crucially, how you replace them in tests:

```python
app.dependency_overrides[get_repository] = lambda: InMemoryRepository()
```

### Errors

```python
raise HTTPException(status_code=404, detail="transaction not found")

# Map a domain exception to a status code once, globally
from fastapi.responses import JSONResponse
from fastapi import Request


@app.exception_handler(ValidationError)
def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

Keep the domain layer free of `HTTPException`: it raises its own exceptions, and the HTTP layer
translates them. That is what lets the same logic serve a CLI and a queue consumer.

### `async def` or `def`?

```python
@app.get("/slow")
async def slow() -> dict[str, str]:
    await asyncio.sleep(1)                # async I/O: fine
    return {"ok": "done"}


@app.get("/db")
def from_db() -> list[TransactionOut]:    # blocking library: use a normal def
    return repository.all()               # FastAPI runs it in a thread pool
```

The rule: `async def` **only** if everything you `await` inside is genuinely async. One blocking
call (a synchronous database driver, `requests`, `time.sleep`) inside an `async def` blocks the
whole event loop and destroys throughput for every request. A plain `def` is safe, because
FastAPI moves it to a worker thread. See [04-concurrency.md](04-concurrency.md).

## Testing an API

```python
from fastapi.testclient import TestClient


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_transaction() -> None:
    response = client.post(
        "/transactions",
        json={"amount": "100.00", "currency": "EUR", "recipient": "Amazon"},
    )
    assert response.status_code == 201
    assert response.json()["recipient"] == "Amazon"


def test_rejects_negative_amount() -> None:
    response = client.post(
        "/transactions",
        json={"amount": "-1", "currency": "EUR", "recipient": "Amazon"},
    )
    assert response.status_code == 422
```

`TestClient` runs the application in-process — no server, no port, no network. These tests are
fast enough to run on every save.

## Project layout

```
src/myservice/
├── api/
│   ├── routes/transactions.py     # APIRouter per resource
│   ├── schemas.py                 # Pydantic In/Out models
│   └── deps.py                    # dependencies
├── domain/                        # business logic, no FastAPI imports
├── db/
└── config.py
```

```python
# api/routes/transactions.py
router = APIRouter(prefix="/transactions", tags=["transactions"])

# api/__init__.py
app.include_router(transactions.router)
```

## Check yourself

1. When do you need Pydantic instead of a dataclass?
2. Why separate the input and output models of an endpoint?
3. What does FastAPI derive automatically from your type annotations?
4. What is the purpose of `Depends`, and how does it help testing?
5. When must an endpoint be `async def`, and when must it not?
6. Why should the domain layer never raise `HTTPException`?
