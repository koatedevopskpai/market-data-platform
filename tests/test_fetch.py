"""Unit tests for the ingestion pipeline."""

import csv
from pathlib import Path

from src.ingestion.fetch_market_data import (
    dedupe_quotes,
    load_csv,
    parse_quotes,
    run,
)

HEADER = ["ticker", "trade_date", "open", "high", "low", "close", "volume"]
ROW = ["AAPL", "2026-10-01", "170.10", "172.50", "169.40", "171.20", "54000000"]


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def test_parse_quotes_returns_errors_for_bad_rows():
    rows = [
        {"ticker": "AAPL", "trade_date": "2026-10-01", "open": "1", "high": "2",
         "low": "0.5", "close": "1.5", "volume": "100"},
        {"ticker": "BAD", "trade_date": "not-a-date", "open": "1", "high": "2",
         "low": "0.5", "close": "1.5", "volume": "100"},
    ]
    valid, errors = parse_quotes(rows)
    assert len(valid) == 1
    assert len(errors) == 1
    assert "line 3" in errors[0]


def test_dedupe_keeps_last_occurrence_per_ticker_and_date():
    rows = [
        {"ticker": "AAPL", "trade_date": "2026-10-01", "open": "1", "high": "2",
         "low": "0.5", "close": "1.5", "volume": "100"},
        {"ticker": "AAPL", "trade_date": "2026-10-01", "open": "9", "high": "9",
         "low": "9", "close": "9", "volume": "900"},
    ]
    valid, _ = parse_quotes(rows)
    deduped = dedupe_quotes(valid)
    assert len(deduped) == 1
    assert str(deduped[0].close) == "9"


def test_run_writes_seeds_and_summary(tmp_path: Path):
    source = tmp_path / "sample"
    source.mkdir()
    out = tmp_path / "seeds"
    _write_csv(source / "market_quotes.csv", HEADER, [ROW])
    _write_csv(
        source / "company_fundamentals.csv",
        ["ticker", "company_name", "sector", "market_cap"],
        [["AAPL", "Apple Inc.", "Technology", "3500000000000"]],
    )

    summary = run(source, out)

    assert summary["quotes"] == 1
    assert summary["instruments"] == 1
    assert (out / "market_quotes.csv").exists()
    assert (out / "company_fundamentals.csv").exists()
    assert load_csv(out / "market_quotes.csv")[0]["ticker"] == "AAPL"
