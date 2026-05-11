import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def extract_weather(city="London"):
    """
    Extract current weather data for a given city from OpenWeatherMap API.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not found in environment variables")
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"  # Get temperature in Celsius
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    data = response.json()
    
    # Extract relevant fields
    weather_data = {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "wind_direction": data["wind"].get("deg", 0),
        "weather_condition": data["weather"][0]["main"],
        "weather_description": data["weather"][0]["description"],
        "timestamp": pd.to_datetime(data["dt"], unit='s')
    }
    
    return pd.DataFrame([weather_data])

if __name__ == "__main__":
    # For testing, extract weather for a few cities
    cities = ["London", "New York", "Tokyo", "Sydney"]
    all_data = []
    
    for city in cities:
        try:
            df = extract_weather(city)
            all_data.append(df)
            print(f"Successfully extracted weather for {city}")
        except Exception as e:
            print(f"Failed to extract weather for {city}: {e}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        # Save to CSV for dbt to pick up
        os.makedirs("data", exist_ok=True)
        combined_df.to_csv("data/weather_raw.csv", index=False)
        print("Weather data saved to data/weather_raw.csv")