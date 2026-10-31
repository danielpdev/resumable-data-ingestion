from functools import lru_cache
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.core import Ingestion

app = FastAPI(title="resumable-data-ingestion")


@lru_cache
def service():
    return Ingestion()


def guarded(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except PermissionError as e:
        raise HTTPException(403, str(e)) from e
    except ValueError as e:
        raise HTTPException(409, str(e)) from e


class Input(BaseModel):
    content: str = Field(max_length=1000000)
    format: str = Field(default="csv", pattern="^(csv|json)$")
    limit: int | None = Field(default=None, ge=1)


@app.post("/api/import")
def ingest(b: Input):
    return guarded(service().ingest, b.content, b.format, b.limit)


@app.get("/api/customers")
def customers():
    return service().customers()


@app.get("/api/quarantine")
def quarantine():
    return service().quarantine()
