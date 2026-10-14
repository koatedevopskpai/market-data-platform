# ADR 0001: Dual target - DuckDB locally, BigQuery in production

- **Status:** Accepted
- **Date:** 2026-10

## Context

The platform targets Google BigQuery, but contributors (and CI) should be able to run and test the entire
transformation DAG without a GCP project, service account, or billed query.

## Decision

Support two dbt targets behind one codebase:

- `local` - the **DuckDB** adapter, writing to a local file (`target/market_data.duckdb`). Used for development and
  CI, no credentials required.
- `bigquery` - the production target, authenticating with OAuth locally or Workload Identity Federation in CI.

Cross-database differences are isolated in dispatched macros (`numeric_type()`, `string_type()`). BigQuery-specific
physical design (partitioning, clustering) is applied only when `target.type == 'bigquery'`.

## Consequences

- CI runs `dbt seed && dbt build` on DuckDB and stays green with no secrets.
- The same models compile on BigQuery; a BigQuery smoke job can be added when credentials are available.
- Contributors must avoid BigQuery-only SQL in model bodies (kept portable via ANSI SQL + macros).
- DuckDB and BigQuery are not byte-identical in every edge case, so production runs should still be smoke-tested.
