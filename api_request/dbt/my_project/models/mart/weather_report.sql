{{ config(
    materialized='table',
    unique_key='id'
) }}

select
    city,
    temperature,
    weather_descriptions,
    wind_speed,
    weather_time_local,
    inserted_at_local
from {{ ref('stg_weather_report') }}