# Architecture

## Layers

```
source -> ingestion -> raw seeds -> dbt (staging -> intermediate -> marts) -> consumers
```

| Layer        | Responsibility                                                       | Where                          |
| ------------ | -------------------------------------------------------------------- | ------------------------------ |
| Ingestion    | Fetch source data, validate with Pydantic v2, de-duplicate           | `src/ingestion/`               |
| Raw          | Validated CSVs loaded as dbt seeds (or a `raw` BigQuery dataset)     | `dbt_platform/seeds/`          |
| Staging      | Cast, rename, de-duplicate to one clean row per key                  | `dbt_platform/models/staging`  |
| Intermediate | Derived metrics: daily return, rolling 30d volatility, 30d VWAP      | `.../intermediate`             |
| Marts        | Kimball star schema (fact + dimension) + the AI retrieval view       | `.../marts`                    |
| Consumers    | Looker Studio dashboards; RAG / LLM retrieval via `mart_ai_equity_context` | external                 |

## Data flow

1. **Ingestion** (`python -m src.ingestion.fetch_market_data`) reads the source directory, validates every row
   against `MarketQuote` / `CompanyFundamental`, drops duplicates (last write wins per `ticker` + `trade_date`) and
   writes normalised CSVs into `dbt_platform/seeds/`. Invalid rows fail the run loudly rather than entering the
   warehouse.
2. **dbt seeds** load those CSVs into the `raw` schema.
3. **Staging models** produce typed, de-duplicated views.
4. **Intermediate** computes windowed metrics. The first 29 rows per instrument have null rolling values by design
   (insufficient history) - consumers must tolerate this.
5. **Marts** publish the star schema:
   - `dim_instruments` - one row per instrument (Type-1).
   - `fct_daily_market_performance` - one row per instrument per day; partitioned by `trade_date` and clustered by
     `ticker` on BigQuery.
   - `mart_ai_equity_context` - the same facts rendered as natural-language rows (`context_text`) plus numerics, for
     retrieval / LLM grounding.

## Design decisions

- **Deterministic-first.** All transformation logic lives in version-controlled SQL; the fact that a metric cannot be
  traced to a model is treated as a defect.
- **Dual target (DuckDB local / BigQuery prod).** The whole DAG runs and is tested in CI without cloud credentials,
  using the DuckDB adapter. See [ADR 0001](adr/0001-dual-target-duckdb-bigquery.md).
- **Tests as a release gate.** Schema and relationship tests run inside `dbt build`; a failing test fails the build.
- **Cost-aware by construction.** BigQuery tables are partitioned and clustered; local development uses DuckDB so no
  query bytes are billed during iteration.
- **Boundary validation.** Source data is validated once, at ingestion, so downstream models can assume clean inputs.

## Portability

Cross-database type differences are handled by dispatched macros in `dbt_platform/macros/types.sql`
(`numeric_type()`, `string_type()`), so one codebase compiles on both DuckDB and BigQuery. BigQuery-only config
(partitioning / clustering) is guarded with `{% if target.type == 'bigquery' %}`.
