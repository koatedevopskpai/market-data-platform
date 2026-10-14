with quotes as (

    select * from {{ ref('stg_market_quotes') }}

),

metrics as (

    select
        ticker,
        trade_date,
        close_price,
        volume,
        lag(close_price) over (
            partition by ticker order by trade_date
        ) as prev_close,
        avg(close_price) over (
            partition by ticker order by trade_date
            rows between 29 preceding and current row
        ) as rolling_30d_avg_close,
        stddev_samp(close_price) over (
            partition by ticker order by trade_date
            rows between 29 preceding and current row
        ) as rolling_30d_volatility,
        sum(close_price * volume) over (
            partition by ticker order by trade_date
            rows between 29 preceding and current row
        ) as rolling_30d_turnover,
        sum(volume) over (
            partition by ticker order by trade_date
            rows between 29 preceding and current row
        ) as rolling_30d_volume
    from quotes

),

final as (

    select
        ticker,
        trade_date,
        close_price,
        volume,
        case
            when prev_close is not null and prev_close <> 0
            then (close_price - prev_close) / prev_close
        end as daily_return,
        rolling_30d_avg_close,
        rolling_30d_volatility,
        case
            when rolling_30d_volume > 0
            then rolling_30d_turnover / rolling_30d_volume
        end as vwap_30d
    from metrics

)

select * from final
