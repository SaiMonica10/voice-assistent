"""
tools/weather.py — Real-time Weather Tool for JARVIS

Uses OpenWeatherMap API (free tier: 60 calls/min, 1M calls/month).
Get your free key at: https://openweathermap.org/api

Learning note:
This demonstrates REST API integration — one of the most fundamental
skills in software development. We make an HTTP GET request, parse
the JSON response, and format it for the LLM to present to the user.
"""

import requests
import config


BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str = None) -> str:
    """
    Fetch current weather for a city.

    Args:
        city: City name (e.g. "Mumbai", "London"). Defaults to config.DEFAULT_CITY.

    Returns:
        A human-readable weather summary string.
    """
    if not config.WEATHER_API_KEY:
        return (
            "Weather tool is not configured. "
            "Please add WEATHER_API_KEY to your .env file. "
            "Get a free key at openweathermap.org"
        )

    target_city = city or config.DEFAULT_CITY

    try:
        response = requests.get(
            BASE_URL,
            params={
                "q": target_city,
                "appid": config.WEATHER_API_KEY,
                "units": "metric",   # Celsius — change to "imperial" for Fahrenheit
            },
            timeout=5,  # Don't hang forever
        )

        # HTTP 200 = success, anything else = error
        if response.status_code == 404:
            return f"City '{target_city}' not found. Please check the city name."
        if response.status_code == 401:
            return "Invalid OpenWeatherMap API key. Check your WEATHER_API_KEY."

        response.raise_for_status()
        data = response.json()

        # Parse the JSON response
        # Learning note: This is what the API returns and how we extract useful info
        weather_main   = data["weather"][0]["main"]           # e.g. "Clouds"
        description    = data["weather"][0]["description"]    # e.g. "overcast clouds"
        temp           = round(data["main"]["temp"])          # Current temp in °C
        feels_like     = round(data["main"]["feels_like"])    # "Feels like" temp
        humidity       = data["main"]["humidity"]             # Humidity %
        wind_speed     = round(data["wind"]["speed"] * 3.6)  # m/s → km/h
        visibility_km  = data.get("visibility", 0) / 1000    # Metres → Km

        # Map weather conditions to emojis for a nicer response
        emoji_map = {
            "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️",
            "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️",
            "Mist": "🌫️", "Haze": "🌫️", "Fog": "🌫️",
        }
        emoji = emoji_map.get(weather_main, "🌡️")

        return (
            f"{emoji} Weather in {target_city}:\n"
            f"  • Condition: {description.capitalize()}\n"
            f"  • Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"  • Humidity: {humidity}%\n"
            f"  • Wind: {wind_speed} km/h\n"
            f"  • Visibility: {visibility_km:.1f} km"
        )

    except requests.Timeout:
        return "Weather service timed out. Please try again."
    except requests.RequestException as e:
        return f"Failed to fetch weather: {str(e)}"
