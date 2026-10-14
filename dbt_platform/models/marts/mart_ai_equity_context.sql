{{ config(materialized='table') }}

-- Retrieval view for the downstream RAG / LLM layer: one natural-language
-- context row per instrument per day, alongside the underlying numerics.

with performance as (

    select * from {{ ref('fct_daily_market_performance') }}

)

select
    market_performance_key,
    ticker,
    company_name,
    sector,
    trade_date,
    close_price,
    daily_return,
    rolling_30d_volatility,
    'On ' || cast(trade_date as {{ string_type() }}) || ', '
        || company_name || ' (' || sector || ') closed at '
        || cast(round(close_price, 2) as {{ string_type() }})
        || ' with a daily return of '
        || cast(round(coalesce(daily_return, 0) * 100, 2) as {{ string_type() }})
        || '%.' as context_text
from performance
