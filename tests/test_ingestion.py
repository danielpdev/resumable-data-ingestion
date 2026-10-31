import json
import pytest
from app.core import Ingestion


def test_resume_deduplicate_and_reprocess(tmp_path):
    url = "sqlite:///" + str(tmp_path / "i.sqlite")
    s = Ingestion(url)
    content = "id,name,email\n1,Alex,a@example.test\n2,Sam,bad\n1,Alex,a@example.test\n"
    assert s.ingest(content, limit=1)["cursor"] == 1
    s = Ingestion(url)
    r = s.ingest(content)
    assert r["done"] and r["customers"] == 1 and r["quarantined"] == 1
    assert s.ingest(content) == r
    s.ingest(json.dumps([{"id": "2", "name": "Sam", "email": "s@example.test"}]), "json")
    assert len(s.customers()) == 2 and len(s.quarantine()) == 1


def test_invalid_json_schema(tmp_path):
    s = Ingestion("sqlite:///" + str(tmp_path / "i.sqlite"))
    with pytest.raises(ValueError):
        s.ingest("{}", "json")
    assert s.ingest('[{"id":"a","name":"A","email":"a@example.test","extra":42}]', "json")["quarantined"] == 1
