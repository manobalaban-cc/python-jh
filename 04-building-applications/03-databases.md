# 03 — Databases

You know SQL. This chapter is about the Python side: the DB-API, SQLAlchemy, and the mistakes
that cause data loss or SQL injection.

## `sqlite3` — the standard library

Every Python database driver implements the same interface (PEP 249), so this pattern transfers
to `psycopg` (PostgreSQL), `mysqlclient` and the rest.

```python
import sqlite3
from pathlib import Path

with sqlite3.connect("transactions.db") as connection:
    connection.row_factory = sqlite3.Row          # rows behave like dicts
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id        INTEGER PRIMARY KEY,
            timestamp TEXT    NOT NULL,
            amount    REAL    NOT NULL,
            currency  TEXT    NOT NULL,
            recipient TEXT    NOT NULL
        )
        """
    )

    cursor.execute(
        "INSERT INTO transactions (timestamp, amount, currency, recipient) VALUES (?, ?, ?, ?)",
        ("2024-05-01 10:00:00", 250.5, "EUR", "Amazon"),
    )

    cursor.executemany(
        "INSERT INTO transactions (timestamp, amount, currency, recipient) VALUES (?, ?, ?, ?)",
        rows,                                     # a list of tuples - one round trip
    )

    for row in cursor.execute("SELECT * FROM transactions WHERE amount > ?", (100,)):
        print(row["recipient"], row["amount"])
```

### Never build SQL with string formatting

```python
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")     # SQL INJECTION
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))    # correct
```

The parameter form is not only safe, it is faster (the statement can be cached) and it handles
quoting, `NULL` and types for you. Note the trailing comma: `(name,)` is a one-element tuple.

Placeholder styles differ by driver — `?` in SQLite, `%s` in psycopg. The rule is the same.

### Transactions

```python
connection = sqlite3.connect("transactions.db")
try:
    cursor = connection.cursor()
    cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100, 1))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (100, 2))
    connection.commit()
except Exception:
    connection.rollback()
    raise
finally:
    connection.close()
```

The `with sqlite3.connect(...)` form commits on success and rolls back on an exception — but
note that it does **not** close the connection, which surprises everyone once.

## SQLAlchemy 2.0

The standard database toolkit for Python. Two layers: **Core** (SQL expressions) and the
**ORM** (objects mapped to rows). Both are worth knowing.

### Core

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///transactions.db", echo=False)

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT recipient, SUM(amount) AS total FROM transactions GROUP BY recipient"),
    )
    for row in result:
        print(row.recipient, row.total)

with engine.begin() as conn:                      # begin() commits at the end of the block
    conn.execute(
        text("INSERT INTO transactions (amount, currency) VALUES (:amount, :currency)"),
        [{"amount": 10, "currency": "EUR"}, {"amount": 20, "currency": "USD"}],
    )
```

Connection URLs:

```
sqlite:///local.db
postgresql+psycopg://user:password@localhost:5432/mydb
mysql+pymysql://user:password@localhost/mydb
```

### ORM

```python
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


class Base(DeclarativeBase):
    pass


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="recipient")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime]
    amount: Mapped[Decimal]
    currency: Mapped[str] = mapped_column(String(3))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("recipients.id"))

    recipient: Mapped[Recipient] = relationship(back_populates="transactions")

    def __repr__(self) -> str:
        return f"Transaction(id={self.id!r}, amount={self.amount!r}, currency={self.currency!r})"


Base.metadata.create_all(engine)        # fine for a demo; real projects use migrations
```

Querying with the 2.0 style — `select()` everywhere, no legacy `Query` object:

```python
with Session(engine) as session:
    stmt = (
        select(Transaction)
        .where(Transaction.amount > 100)
        .order_by(Transaction.timestamp.desc())
        .limit(10)
    )
    for transaction in session.scalars(stmt):
        print(transaction)

    # Aggregation
    from sqlalchemy import func

    stmt = (
        select(Recipient.name, func.sum(Transaction.amount).label("total"))
        .join(Transaction)
        .group_by(Recipient.name)
        .order_by(func.sum(Transaction.amount).desc())
    )
    for name, total in session.execute(stmt):
        print(name, total)
```

Writing:

```python
with Session(engine) as session:
    recipient = Recipient(name="Amazon")
    session.add(recipient)
    session.add(Transaction(timestamp=datetime.now(), amount=Decimal("99.90"),
                            currency="EUR", recipient=recipient))
    session.commit()                    # one transaction for both inserts
```

### The N+1 problem

```python
for transaction in session.scalars(select(Transaction)):
    print(transaction.recipient.name)       # one extra SELECT per row!
```

The relationship is loaded lazily, so a thousand rows mean a thousand and one queries. Load it
in one go:

```python
from sqlalchemy.orm import selectinload, joinedload

stmt = select(Transaction).options(selectinload(Transaction.recipient))
```

This is the single most common performance bug in ORM code, in any language. Turn on
`echo=True` during development and watch the queries — if you see the same statement repeating,
you found it.

## Migrations

`Base.metadata.create_all()` creates tables that do not exist; it never changes an existing one.
For a real project use **Alembic**:

```bash
alembic init migrations
alembic revision --autogenerate -m "add transactions table"
alembic upgrade head
alembic downgrade -1
```

Review every autogenerated migration before committing it — Alembic guesses, and it cannot know
that a rename is a rename rather than a drop plus an add.

## Repository pattern

Keep SQL out of the business logic by hiding it behind an interface:

```python
class TransactionRepository(Protocol):
    def add(self, transaction: Transaction) -> None: ...
    def find_large(self, threshold: Decimal) -> list[Transaction]: ...


class SqlTransactionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, transaction: Transaction) -> None:
        self._session.add(transaction)

    def find_large(self, threshold: Decimal) -> list[Transaction]:
        return list(self._session.scalars(select(Transaction).where(Transaction.amount >= threshold)))
```

The payoff: unit tests use an in-memory implementation and run in milliseconds; integration
tests use a real database through the same interface.

## Testing database code

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")      # a fresh database per test
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

An in-memory SQLite database is the pragmatic default. When your production database is
PostgreSQL and you rely on its specific features, run the integration tests against a real
PostgreSQL in a container (`testcontainers`) — SQLite will not catch dialect differences.

## Rules that prevent incidents

1. **Parameters, never string formatting.**
2. **One transaction per unit of work**, and `rollback()` on failure.
3. **Never `SELECT *` in application code** — an added column silently changes your result shape.
4. **Never run `DELETE`/`UPDATE` without a `WHERE`.** Write the `SELECT` first and look at it.
5. **Connection strings come from the environment**, never from the source.
6. **Close connections** — use a context manager or a connection pool.
7. **Paginate.** `LIMIT`/`OFFSET` or keyset pagination; do not load a million rows into a list.

## Check yourself

1. Why is `cursor.execute(f"... {value}")` dangerous, and what replaces it?
2. What does `with engine.begin()` do that `with engine.connect()` does not?
3. What is the N+1 problem and how do you detect and fix it?
4. Why is `Base.metadata.create_all()` not enough for a real project?
5. What does the repository pattern buy you in tests?
6. Why avoid `SELECT *` in application code?
