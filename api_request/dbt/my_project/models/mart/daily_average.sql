{{  config(
    materialized='table',
)}}

select
    city,
    date(weather_time_local) as weather_date,
    round(avg(temperature::numeric), 2) as avg_temperature,
    round(avg(wind_speed::numeric), 2) as avg_wind_speed
from {{ ref('stg_weather_report') }}
group by city, weather_date
order by city, weather_date