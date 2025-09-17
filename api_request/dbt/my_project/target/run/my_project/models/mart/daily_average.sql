
  
    

  create  table "db"."dev"."daily_average__dbt_tmp"
  
  
    as
  
  (
    

select
    city,
    date(weather_time_local) as weather_date,
    round(avg(temperature::numeric), 2) as avg_temperature,
    round(avg(wind_speed::numeric), 2) as avg_wind_speed
from "db"."dev"."stg_weather_report"
group by city, weather_date
order by city, weather_date
  );
  