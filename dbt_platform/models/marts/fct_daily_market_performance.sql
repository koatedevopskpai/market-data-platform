{% if target.type == 'bigquery' %}
{{ config(
    materialized='table',
    partition_by={'field': 'trade_date', 'data_type': 'date'},
    cluster_by=['ticker']
) }}
{% else %}
{{ config(materialized='table') }}
{% endif %}

with metrics as (

    select * from {{ ref('int_daily_price_metrics') }}

),

instruments as (

    select * from {{ ref('dim_instruments') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['m.ticker', 'm.trade_date']) }} as market_performance_key,
    m.ticker,
    i.company_name,
    i.sector,
    m.trade_date,
    m.close_price,
    m.daily_return,
    m.rolling_30d_volatility,
    m.vwap_30d,
    m.volume
from metrics as m
left join instruments as i using (ticker)
