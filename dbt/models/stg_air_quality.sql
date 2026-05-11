-- Staging model for air quality data
-- Cleans and standardizes the raw air quality data

with source_data as (
    select * from {{ ref('air_quality_raw') }}
),

cleaned as (
    select
        city,
        state,
        country,
        aqi,
        main_pollutant,
        temperature as temp_c,
        humidity,
        pressure,
        wind_speed,
        wind_direction,
        weather_condition,
        timestamp as aq_timestamp
    from source_data
    where aqi is not null  -- Basic validation
)

select * from cleaned