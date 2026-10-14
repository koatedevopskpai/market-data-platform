with source as (

    select * from {{ ref('market_quotes') }}

),

renamed as (

    select
        upper(trim(ticker))                  as ticker,
        cast(trade_date as date)             as trade_date,
        cast(open  as {{ numeric_type() }})  as open_price,
        cast(high  as {{ numeric_type() }})  as high_price,
        cast(low   as {{ numeric_type() }})  as low_price,
        cast(close as {{ numeric_type() }})  as close_price,
        cast(volume as bigint)               as volume
    from source

),

deduped as (

    select
        *,
        row_number() over (
            partition by ticker, trade_date
            order by close_price desc
        ) as row_num
    from renamed

)

select ticker, trade_date, open_price, high_price, low_price, close_price, volume
from deduped
where row_num = 1
