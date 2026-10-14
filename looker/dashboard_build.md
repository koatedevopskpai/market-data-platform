# Looker Studio — build guide

The BI layer connects Looker Studio directly to the BigQuery `marts` dataset produced by dbt.

## Connect

1. Looker Studio → **Create** → **Report** → **Add data** → **BigQuery**.
2. Choose your project → dataset `market_data_marts` → table `fct_daily_market_performance` → **Add**.
3. Add a second data source: `dim_instruments` (for instrument attributes / drill-down).

## Page 1 — Market Overview

- **Scorecards:** latest close, mean daily return, mean 30-day volatility (blended).
- **Time series:** `rolling_30d_volatility` by `trade_date`, split by `ticker`.
- **Table:** top movers — `ticker`, `close_price`, `daily_return`, sorted descending by absolute `daily_return`.
- **Filter control:** `sector`.

## Page 2 — Trend Analysis

- **Combo chart:** `close_price` (line) and `vwap_30d` (line) over `trade_date`, by `ticker`.
- **Time series:** `rolling_30d_volatility` by `sector`.
- **Date-range control:** last 30 / 90 days.

## Page 3 — Instrument Detail (drill-down)

- **Scorecards:** company name, sector, market cap (from `dim_instruments`).
- **Time series:** price and volume for the selected `ticker` (use a report parameter + control).
- **Table:** the `mart_ai_equity_context.context_text` rows for context / narrative.

## Screenshots

After building, export each page to PNG and drop them in `looker/screenshots/`:

```
looker/screenshots/
├── 01-market-overview.png
├── 02-trend-analysis.png
└── 03-instrument-detail.png
```

Then reference them at the top of the root `README.md`.

## Notes

- Looker Studio is the reporting surface only; all modelling happens in dbt. Never model in the BI tool.
- Because `fct_daily_market_performance` is partitioned by `trade_date`, dashboards default to a recent date range to
  keep BigQuery scan costs low.
