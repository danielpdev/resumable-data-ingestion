# Design record

## Decision

A batch ID hashes the immutable source content. Each row effect, validation failure and cursor update commit together. Bad rows enter quarantine; corrected input is a new batch and upserts the same business ID.

## Failure model

Partial import then restart, duplicate business IDs, malformed rows, corrected records, retained quarantine and PostgreSQL execution.

## Tradeoffs

Inputs are bounded and loaded into memory. SQLite mode assumes one importer per batch; PostgreSQL locks the batch row. Upserts use source order, not a cross-source conflict policy.

## Next change to defend in review

Add streaming input, source provenance, distributed leases and explicit conflict policy.

## Reproducibility

`uv.lock` pins Python dependencies; the web lockfile pins the React build where present. Model-backed evaluations use a separately installed local service. Dataset examples are synthetic and intentionally small. Reported timing is a local observation, not a throughput SLA. Run `make test` after changing state transitions and `make eval` after changing decisions. Keep inference quality separate from deterministic invariant checks.
