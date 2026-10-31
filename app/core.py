"""Checkpoint and row effect commit together; each immutable input is a distinct batch."""

import csv
import hashlib
import io
import json
import tempfile
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base, database


class CustomerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class Batch(Base):
    __tablename__ = "batches"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    cursor: Mapped[int]
    total: Mapped[int]


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    body: Mapped[str]


class Quarantine(Base):
    __tablename__ = "quarantine"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    batch: Mapped[str]
    row_number: Mapped[int]
    raw: Mapped[str]
    reason: Mapped[str]


class Ingestion:
    def __init__(self, url=None):
        self.engine, self.sessions = database(url)

    def ingest(self, content, format="csv", limit=None):
        if format not in {"csv", "json"}:
            raise ValueError("format must be csv or json")
        rows = list(csv.DictReader(io.StringIO(content))) if format == "csv" else json.loads(content)
        if not isinstance(rows, list):
            raise ValueError("JSON input must be an array")
        bid = hashlib.sha256((format + "\0" + content).encode()).hexdigest()
        with self.sessions.begin() as s:
            if not s.get(Batch, bid):
                s.add(Batch(id=bid, cursor=0, total=len(rows)))
        count = 0
        while limit is None or count < limit:
            with self.sessions.begin() as s:
                b = s.scalar(select(Batch).where(Batch.id == bid).with_for_update())
                if b.cursor >= b.total:
                    break
                row = rows[b.cursor]
                try:
                    item = CustomerInput.model_validate(row)
                    old = s.get(Customer, item.id)
                    if old:
                        old.body = item.model_dump_json()
                    else:
                        s.add(Customer(id=item.id, body=item.model_dump_json()))
                except ValidationError as exc:
                    s.add(
                        Quarantine(
                            key=f"{bid}:{b.cursor}",
                            batch=bid,
                            row_number=b.cursor + 1,
                            raw=json.dumps(row),
                            reason=str(exc),
                        )
                    )
                b.cursor += 1
            count += 1
        return self.status(bid)

    def status(self, bid):
        with self.sessions() as s:
            b = s.get(Batch, bid)
            return dict(
                batch=bid,
                cursor=b.cursor,
                total=b.total,
                done=b.cursor == b.total,
                customers=len(list(s.scalars(select(Customer)))),
                quarantined=len(list(s.scalars(select(Quarantine).where(Quarantine.batch == bid)))),
            )

    def customers(self):
        with self.sessions() as s:
            return [json.loads(c.body) for c in s.scalars(select(Customer).order_by(Customer.id))]

    def quarantine(self):
        with self.sessions() as s:
            return [
                dict(batch=q.batch, row=q.row_number, raw=json.loads(q.raw), reason=q.reason)
                for q in s.scalars(select(Quarantine))
            ]


def demo(mode="fixture"):
    with tempfile.TemporaryDirectory() as d:
        url = "sqlite:///" + str(Path(d) / "import.sqlite")
        s = Ingestion(url)
        content = Path("data/customers.csv").read_text()
        partial = s.ingest(content, limit=2)
        s = Ingestion(url)
        done = s.ingest(content)
        corrected = s.ingest('[{"id":"3","name":"Invalid corrected","email":"fixed@example.test"}]', "json")
        return dict(
            checkpoint=partial,
            resumed=done,
            corrected=corrected,
            customers=s.customers(),
            quarantine=s.quarantine(),
        )


def evaluate(mode="fixture"):
    r = demo(mode)
    return dict(
        passed=r["resumed"]["customers"] == 2
        and r["resumed"]["quarantined"] == 1
        and len(r["customers"]) == 3,
        scenario=r,
    )
