

with source as (
        select * 
        from "db"."dev"."raw_weather_data"
)

select
    id,
    city,
    temperature,
    weather_descriptions,
    wind_speed,
    time as weather_time_local,
    (inserted_at + (utc_offset || 'hours')::interval) as inserted_at_local
from source