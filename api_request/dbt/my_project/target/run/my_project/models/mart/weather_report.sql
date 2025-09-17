
  
    

  create  table "db"."dev"."weather_report__dbt_tmp"
  
  
    as
  
  (
    

select
    city,
    temperature,
    weather_descriptions,
    wind_speed,
    weather_time_local,
    inserted_at_local
from "db"."dev"."stg_weather_report"
  );
  