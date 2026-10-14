with source as (

    select * from {{ ref('company_fundamentals') }}

)

select
    upper(trim(ticker))                       as ticker,
    trim(company_name)                        as company_name,
    trim(sector)                              as sector,
    cast(market_cap as {{ numeric_type() }})  as market_cap
from source
