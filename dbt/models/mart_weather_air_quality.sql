-- Mart model combining weather and air quality data
-- Joins weather and air quality data by city and date

with weather as (
    select * from {{ ref('stg_weather') }}
),

air_quality as (
    select * from {{ ref('stg_air_quality') }}
),

-- Since the timestamps might not match exactly, we'll join on city and the date part
joined as (
    select
        w.city,
        w.country,
        w.temperature as weather_temperature,
        w.feels_like,
        w.humidity as weather_humidity,
        w.pressure,
        w.wind_speed,
        w.wind_direction,
        w.weather_condition,
        w.weather_description,
        w.weather_timestamp,
        a.state,
        a.aqi,
        a.main_pollutant,
        a.temp_c as aq_temperature,
        a.humidity as aq_humidity,
        a.pressure as aq_pressure,
        a.wind_speed as aq_wind_speed,
        a.wind_direction as aq_wind_direction,
        a.weather_condition as aq_weather_condition,
        a.aq_timestamp
    from weather w
    left join air_quality a
        on w.city = a.city
        and date(w.weather_timestamp) = date(a.aq_timestamp)
)

select * from joined