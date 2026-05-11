import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def extract_air_quality(city="London", state="", country="UK"):
    """
    Extract current air quality data for a given city from AirVisual API.
    """
    api_key = os.getenv("AIRVISUAL_API_KEY")
    if not api_key:
        raise ValueError("AIRVISUAL_API_KEY not found in environment variables")
    
    base_url = "http://api.airvisual.com/v2/city"
    params = {
        "city": city,
        "state": state,
        "country": country,
        "key": api_key
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    if data["status"] != "success":
        raise Exception(f"API returned error: {data}")
    
    # Extract relevant fields from the response
    current = data["data"]["current"]
    pollution = current["pollution"]
    weather = current["weather"]
    
    air_quality_data = {
        "city": data["data"]["city"],
        "state": data["data"]["state"],
        "country": data["data"]["country"],
        "aqi": pollution["aqius"],
        "main_pollutant": pollution["mainus"],
        "temperature": weather["tp"],
        "humidity": weather["hu"],
        "pressure": weather["pr"],
        "wind_speed": weather["ws"],
        "wind_direction": weather["wd"],
        "weather_condition": weather["ic"],  # Icon code, could be mapped to description
        "timestamp": pd.to_datetime(current["weather"]["ts"])
    }
    
    return pd.DataFrame([air_quality_data])

if __name__ == "__main__":
    # For testing, extract air quality for a few cities
    cities = [
        {"city": "London", "state": "", "country": "UK"},
        {"city": "New York", "state": "NY", "country": "USA"},
        {"city": "Tokyo", "state": "", "country": "JP"},
        {"city": "Sydney", "state": "NSW", "country": "AU"}
    ]
    
    all_data = []
    
    for location in cities:
        try:
            df = extract_air_quality(**location)
            all_data.append(df)
            print(f"Successfully extracted air quality for {location['city']}")
        except Exception as e:
            print(f"Failed to extract air quality for {location['city']}: {e}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        # Save to CSV for dbt to pick up
        os.makedirs("data", exist_ok=True)
        combined_df.to_csv("data/air_quality_raw.csv", index=False)
        print("Air quality data saved to data/air_quality_raw.csv")