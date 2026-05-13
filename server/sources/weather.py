"""OpenWeatherMap source.

Supported conditions:
    rain_today      → any rain/drizzle/thunderstorm in today's forecast
    rain_now        → currently raining
    temp_above:N    → current temperature strictly greater than N °C
    temp_below:N    → current temperature strictly less than N °C
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from server.config import settings
from server.sources.base import Source

_RAIN_GROUPS = {"Rain", "Drizzle", "Thunderstorm"}


class WeatherSource(Source):
    name = "weather"

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    async def check(
        self,
        config: dict[str, Any],
        *,
        recipe_name: str,
    ) -> tuple[bool, dict[str, Any]]:
        location = config.get("location")
        condition = config.get("condition", "rain_today")
        api_key = config.get("api_key") or settings.openweather_api_key

        if not location:
            raise RuntimeError("weather source requires 'location' (e.g. 'Lima, PE')")
        if not api_key:
            raise RuntimeError(
                "OpenWeatherMap api_key not set. Configure OPENWEATHER_API_KEY in .env."
            )

        if condition == "rain_now" or condition.startswith(("temp_above", "temp_below")):
            data = await self._fetch(f"{self.BASE_URL}/weather", location, api_key)
            return self._evaluate_current(data, condition)

        if condition == "rain_today":
            data = await self._fetch(f"{self.BASE_URL}/forecast", location, api_key)
            return self._evaluate_forecast_today(data)

        raise RuntimeError(f"weather: unsupported condition '{condition}'")

    async def _fetch(self, url: str, location: str, api_key: str) -> dict[str, Any]:
        params = {"q": location, "appid": api_key, "units": "metric", "lang": "es"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def _evaluate_current(
        data: dict[str, Any], condition: str
    ) -> tuple[bool, dict[str, Any]]:
        weather = (data.get("weather") or [{}])[0]
        main = weather.get("main", "")
        description = weather.get("description", "")
        temp_c = float(data.get("main", {}).get("temp", 0))
        feels_like_c = float(data.get("main", {}).get("feels_like", 0))
        humidity = data.get("main", {}).get("humidity")
        city = data.get("name", "")

        ctx = {
            "location": city,
            "city": city,
            "temp_c": temp_c,
            "feels_like_c": feels_like_c,
            "humidity": humidity,
            "description": description,
            "weather_main": main,
        }

        if condition == "rain_now":
            return main in _RAIN_GROUPS, ctx

        if condition.startswith("temp_above:"):
            threshold = float(condition.split(":", 1)[1])
            return temp_c > threshold, ctx
        if condition.startswith("temp_below:"):
            threshold = float(condition.split(":", 1)[1])
            return temp_c < threshold, ctx

        raise RuntimeError(f"weather: unsupported condition '{condition}'")

    @staticmethod
    def _evaluate_forecast_today(data: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        city = data.get("city", {}).get("name", "")
        tz_offset = data.get("city", {}).get("timezone", 0)
        today_local = datetime.now(timezone.utc).timestamp() + tz_offset
        today_date = datetime.fromtimestamp(today_local, tz=timezone.utc).date()

        max_precip = 0.0
        rain_entry: dict[str, Any] | None = None
        for entry in data.get("list", []):
            entry_local_ts = entry.get("dt", 0) + tz_offset
            entry_date = datetime.fromtimestamp(entry_local_ts, tz=timezone.utc).date()
            if entry_date != today_date:
                continue
            weather = (entry.get("weather") or [{}])[0]
            main = weather.get("main", "")
            precip = float(entry.get("rain", {}).get("3h", 0))
            if main in _RAIN_GROUPS or precip > 0:
                if rain_entry is None:
                    rain_entry = entry
                max_precip = max(max_precip, precip)

        ctx: dict[str, Any] = {
            "location": city,
            "city": city,
            "precipitation_mm": max_precip,
        }
        if rain_entry is None:
            return False, ctx

        weather = (rain_entry.get("weather") or [{}])[0]
        ctx["description"] = weather.get("description", "")
        ctx["weather_main"] = weather.get("main", "")
        ctx["temp_c"] = float(rain_entry.get("main", {}).get("temp", 0))
        return True, ctx
