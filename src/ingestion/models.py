"""Pydantic v2 data contracts for the market-data ingestion layer.

Every row that enters the platform is validated against one of these models, so
malformed source data fails fast at the boundary rather than corrupting the
warehouse.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class MarketQuote(BaseModel):
    """A single daily OHLCV quote for one instrument."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    ticker: str = Field(min_length=1, max_length=10)
    trade_date: date
    open: Decimal = Field(ge=0)
    high: Decimal = Field(ge=0)
    low: Decimal = Field(ge=0)
    close: Decimal = Field(ge=0)
    volume: int = Field(ge=0)

    @field_validator("ticker")
    @classmethod
    def normalise_ticker(cls, value: str) -> str:
        return value.strip().upper()

    @model_validator(mode="after")
    def check_price_bounds(self) -> MarketQuote:
        if self.high < self.low:
            raise ValueError(f"high ({self.high}) is below low ({self.low})")
        if not (self.low <= self.close <= self.high):
            raise ValueError(f"close ({self.close}) outside range [{self.low}, {self.high}]")
        return self


class CompanyFundamental(BaseModel):
    """Static reference data for one instrument."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    ticker: str = Field(min_length=1, max_length=10)
    company_name: str = Field(min_length=1)
    sector: str = Field(min_length=1)
    market_cap: Decimal | None = Field(default=None, ge=0)

    @field_validator("ticker")
    @classmethod
    def normalise_ticker(cls, value: str) -> str:
        return value.strip().upper()
