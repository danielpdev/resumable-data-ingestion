# Demo walkthrough

## Start

```bash
make setup
make demo
make test
make eval
```

## What to show

A batch ID hashes the immutable source content. Each row effect, validation failure and cursor update commit together. Bad rows enter quarantine; corrected input is a new batch and upserts the same business ID.

## Failure case to discuss

Partial import then restart, duplicate business IDs, malformed rows, corrected records, retained quarantine and PostgreSQL execution.

## Evidence

Open the JSON evaluation report alongside the implementation. Distinguish synthetic fixture outputs, synthetic trace timing, actual elapsed evaluation time, and local model inference. Do not present a tiny test set as a production benchmark.

## Closing tradeoff

Inputs are bounded and loaded into memory. SQLite mode assumes one importer per batch; PostgreSQL locks the batch row. Upserts use source order, not a cross-source conflict policy.

The repository's `docs/demo.webm` or `docs/demo.mp4`, when present, records the demonstration. A terminal replay is also available for focused projects as `docs/demo.cast`.
