# Resumable Data Ingestion

Checkpointed CSV/JSON import with quarantine and deduplication.

[![verification](https://github.com/danielpdev/resumable-data-ingestion/actions/workflows/ci.yml/badge.svg)](https://github.com/danielpdev/resumable-data-ingestion/actions/workflows/ci.yml)

**Role focus:** Data Engineer / Python Backend. **Status:** working local portfolio implementation, with synthetic data.

## Demo

![How Resumable Data Ingestion works](docs/demo.gif)

Edited replay of captured CLI outputs in deterministic fixture mode. This is not live model inference. [Full recording](docs/demo.mp4). Rebuild with `./scripts/render_gif.sh` (FFmpeg required).

## The engineering decision

A batch ID hashes the immutable source content. Each row effect, validation failure and cursor update commit together. Bad rows enter quarantine; corrected input is a new batch and upserts the same business ID.

```mermaid
flowchart LR
  CSV_or_JSON --> Immutable_batch; Immutable_batch --> Row_validation; Row_validation --> Customer_upsert; Row_validation --> Quarantine; Transaction --> Cursor_checkpoint
```

## Run locally

Requirements: Python 3.12, [uv](https://docs.astral.sh/uv/getting-started/installation/) and Make.

```bash
git clone https://github.com/danielpdev/resumable-data-ingestion.git
cd resumable-data-ingestion
make setup
make demo
make test
make eval
```

`make demo` uses an isolated temporary database where relevant, so it is safe to repeat. `make eval` writes a timestamped report to `reports/evaluation-fixture.json`. Fixture mode is deterministic and does not represent model inference. There is no recurring hosting or API subscription cost.

`make serve` opens the local API on `http://127.0.0.1:8120/docs`.

### PostgreSQL

The zero-service quickstart uses SQLite. The same SQLAlchemy domain layer also runs on PostgreSQL:

```bash
docker compose up -d postgres
DATABASE_URL=postgresql+psycopg://portfolio:local-demo-only@127.0.0.1:55445/demo make serve
```

`tests/test_postgres.py` uses `POSTGRES_TEST_URL` and drops its test tables during cleanup. Point it only at a dedicated disposable test database. CI provisions one independently. Local demonstration credentials are deliberately non-secret and must never be reused for production.

[Watch the recorded demo](docs/demo.mp4) · [Reproduce the walkthrough](docs/DEMO.md)

## Verification and evidence

Partial import then restart, duplicate business IDs, malformed rows, corrected records, retained quarantine and PostgreSQL execution.

- [Evaluation report](reports/evaluation-fixture.json) — measured during an actual run; inspect the mode and dataset size.
- [Development and authorship](docs/DEVELOPMENT.md).
- [Romanian interview preparation](docs/INTERVIEW_RO.md).
- [Design notes](docs/DESIGN.md).
- [Demo walkthrough](docs/DEMO.md).

CI uses standard GitHub-hosted runners and deterministic tests without downloading LLM weights. The lockfiles record exact package versions. Local-model results, when present, live in `reports/evaluation-local.json`; hardware/model identities are in `reports/environment.json`.

## Limits and next iteration

Inputs are bounded and loaded into memory. SQLite mode assumes one importer per batch; PostgreSQL locks the batch row. Upserts use source order, not a cross-source conflict policy.

Next: Add streaming input, source provenance, distributed leases and explicit conflict policy.

The local demonstration does not include production authentication, secret management or operational service guarantees. Bind it to localhost and use synthetic data. These projects demonstrate engineering decisions; they do not claim real customers, paid production deployments or guaranteed interviews.

## Project ownership

Implemented with Codex assistance for Daniel Popa. The owner should review the code, run it, make an independent change and rehearse the tradeoffs before presenting it at interview. That human understanding check is pending and cannot be verified automatically. See [development notes](docs/DEVELOPMENT.md).

MIT for original source; dependencies/models retain their own licenses. See [third-party notices](THIRD_PARTY.md).
