"""Unit tests for the ingestion data contracts."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.ingestion.models import CompanyFundamental, MarketQuote

VALID = {
    "ticker": "aapl",
    "trade_date": "2026-10-01",
    "open": "170.10",
    "high": "172.50",
    "low": "169.40",
    "close": "171.20",
    "volume": "54000000",
}


def test_valid_quote_parses_and_normalises_ticker():
    quote = MarketQuote.model_validate(VALID)
    assert quote.ticker == "AAPL"
    assert quote.trade_date == date(2026, 10, 1)
    assert quote.close == Decimal("171.20")


def test_high_below_low_is_rejected():
    bad = {**VALID, "high": "160.00"}
    with pytest.raises(ValidationError):
        MarketQuote.model_validate(bad)


def test_close_outside_range_is_rejected():
    bad = {**VALID, "close": "200.00"}
    with pytest.raises(ValidationError):
        MarketQuote.model_validate(bad)


def test_negative_volume_is_rejected():
    bad = {**VALID, "volume": "-1"}
    with pytest.raises(ValidationError):
        MarketQuote.model_validate(bad)


def test_quote_is_immutable():
    quote = MarketQuote.model_validate(VALID)
    with pytest.raises(ValidationError):
        quote.close = Decimal("1.00")


def test_fundamental_market_cap_is_optional():
    fundamental = CompanyFundamental.model_validate(
        {"ticker": "msft", "company_name": "Microsoft", "sector": "Technology"}
    )
    assert fundamental.ticker == "MSFT"
    assert fundamental.market_cap is None
