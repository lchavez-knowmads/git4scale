-- Staging model for weather data
-- Cleans and standardizes the raw weather data

with source_data as (
    select * from {{ ref('weather_raw') }}
),

cleaned as (
    select
        city,
        country,
        temperature,
        feels_like,
        humidity,
        pressure,
        wind_speed,
        wind_direction,
        weather_condition,
        weather_description,
        timestamp as weather_timestamp
    from source_data
    where temperature is not null  -- Basic validation
)

select * from cleaned