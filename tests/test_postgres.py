import os
import pytest
from app.core import Ingestion
from app.db import Base


@pytest.mark.skipif(
    not os.getenv("POSTGRES_TEST_URL"), reason="Set POSTGRES_TEST_URL to a dedicated test database"
)
def test_postgresql_transactional_scenario():
    s = Ingestion(os.environ["POSTGRES_TEST_URL"])
    try:
        from pathlib import Path

        content = Path("data/customers.csv").read_text()
        s.ingest(content, limit=1)
        r = s.ingest(content)
        assert r["done"] and r["customers"] == 2 and r["quarantined"] == 1
    finally:
        Base.metadata.drop_all(s.engine)
        s.engine.dispose()
