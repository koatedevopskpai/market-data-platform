select
    {{ dbt_utils.generate_surrogate_key(['ticker']) }} as instrument_key,
    ticker,
    company_name,
    sector,
    market_cap
from {{ ref('stg_company_fundamentals') }}
