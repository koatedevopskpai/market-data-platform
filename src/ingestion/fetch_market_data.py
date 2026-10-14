"""Ingestion entry point: read a market-data source, validate it with Pydantic,
de-duplicate, and write normalised CSVs that dbt loads as seeds.

The default ``--source`` is a bundled, clearly-labelled synthetic sample so the
whole pipeline runs offline. Point ``--source`` at a directory produced by any
real feed exporter to use live data - the loader interface is unchanged.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable
from pathlib import Path

from pydantic import ValidationError

from src.ingestion.models import CompanyFundamental, MarketQuote

QUOTE_FIELDS = ("ticker", "trade_date", "open", "high", "low", "close", "volume")
FUNDAMENTAL_FIELDS = ("ticker", "company_name", "sector", "market_cap")


def load_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into a list of dict rows."""
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _validate(rows: Iterable[dict[str, str]], model: type, label: str) -> tuple[list, list[str]]:
    valid, errors = [], []
    for line, row in enumerate(rows, start=2):  # line 1 is the header
        try:
            valid.append(model.model_validate(row))
        except ValidationError as exc:
            first = exc.errors()[0]
            errors.append(f"{label} line {line}: {first['loc'][0]} - {first['msg']}")
    return valid, errors


def parse_quotes(rows: Iterable[dict[str, str]]) -> tuple[list[MarketQuote], list[str]]:
    return _validate(rows, MarketQuote, "market_quotes")


def parse_fundamentals(
    rows: Iterable[dict[str, str]],
) -> tuple[list[CompanyFundamental], list[str]]:
    return _validate(rows, CompanyFundamental, "company_fundamentals")


def dedupe_quotes(quotes: Iterable[MarketQuote]) -> list[MarketQuote]:
    """Keep one row per (ticker, trade_date); the last occurrence wins."""
    latest: dict[tuple[str, object], MarketQuote] = {}
    for quote in quotes:
        latest[(quote.ticker, quote.trade_date)] = quote
    return sorted(latest.values(), key=lambda q: (q.ticker, q.trade_date))


def _write(path: Path, fields: tuple[str, ...], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(rows)


def write_quotes(quotes: Iterable[MarketQuote], path: Path) -> None:
    _write(
        path,
        QUOTE_FIELDS,
        (
            {
                "ticker": q.ticker,
                "trade_date": q.trade_date.isoformat(),
                "open": str(q.open),
                "high": str(q.high),
                "low": str(q.low),
                "close": str(q.close),
                "volume": str(q.volume),
            }
            for q in quotes
        ),
    )


def write_fundamentals(fundamentals: Iterable[CompanyFundamental], path: Path) -> None:
    _write(
        path,
        FUNDAMENTAL_FIELDS,
        (
            {
                "ticker": f.ticker,
                "company_name": f.company_name,
                "sector": f.sector,
                "market_cap": "" if f.market_cap is None else str(f.market_cap),
            }
            for f in fundamentals
        ),
    )


def run(source_dir: Path, out_dir: Path) -> dict[str, object]:
    """Validate the source, write normalised seeds, and return a summary."""
    quotes, quote_errors = parse_quotes(load_csv(source_dir / "market_quotes.csv"))
    funds, fund_errors = parse_fundamentals(load_csv(source_dir / "company_fundamentals.csv"))

    errors = quote_errors + fund_errors
    if errors:
        raise SystemExit("Validation failed:\n  " + "\n  ".join(errors))

    quotes = dedupe_quotes(quotes)
    write_quotes(quotes, out_dir / "market_quotes.csv")
    write_fundamentals(funds, out_dir / "company_fundamentals.csv")

    summary = {
        "source": str(source_dir),
        "out": str(out_dir),
        "quotes": len(quotes),
        "instruments": len(funds),
    }
    print(json.dumps(summary, indent=2))
    return summary


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Ingest market data and write dbt seeds.")
    parser.add_argument("--source", type=Path, default=Path("data/sample"))
    parser.add_argument("--out", type=Path, default=Path("dbt_platform/seeds"))
    args = parser.parse_args(argv)
    run(args.source, args.out)


if __name__ == "__main__":
    main()
