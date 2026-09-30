import datetime
from zoneinfo import ZoneInfo
import urllib.request
import urllib.parse
import json

def get_current_time(timezone: str = "UTC") -> str:
    """Returns the current date and time for a given timezone."""
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        tz = ZoneInfo("UTC")
    now = datetime.datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")

tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time. Useful when you need to answer questions about the current time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The timezone to get the time for, e.g. 'UTC', 'America/New_York', 'Asia/Kolkata'"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and country to get the weather for, e.g. 'Visakhapatnam, India' or 'Paris, France'"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

def get_weather(location: str) -> str:
    """Gets the current weather for a given location using Open-Meteo API."""
    try:
        # 1. Geocoding
        safe_loc = urllib.parse.quote(location)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={safe_loc}&count=1&language=en&format=json"
        
        req = urllib.request.Request(geo_url, headers={'User-Agent': 'AntigravityAgent/1.0'})
        with urllib.request.urlopen(req) as response:
            geo_data = json.loads(response.read().decode())
            
        if not geo_data.get("results"):
            return f"Error: Could not find location '{location}'."
            
        result = geo_data["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        name = result["name"]
        
        # 2. Weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        req = urllib.request.Request(weather_url, headers={'User-Agent': 'AntigravityAgent/1.0'})
        with urllib.request.urlopen(req) as response:
            weather_data = json.loads(response.read().decode())
            
        current = weather_data.get("current_weather", {})
        temp = current.get("temperature")
        wind = current.get("windspeed")
        
        return f"Current weather in {name}: Temperature {temp}°C, Wind Speed {wind} km/h."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
