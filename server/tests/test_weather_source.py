"""Tests for WeatherSource.

External HTTP is replaced with a stub that returns canned OWM-shaped data, so
the tests don't hit the network and don't need an API key.
"""
from __future__ import annotations

import time

import pytest

from server.sources.weather import WeatherSource

TODAY_TS = int(time.time())


def _make_source_with_payload(payload: dict) -> WeatherSource:
    src = WeatherSource()

    async def _stub_fetch(self, url, location, api_key):  # noqa: ARG001
        return payload

    src._fetch = _stub_fetch.__get__(src, WeatherSource)  # type: ignore[method-assign]
    return src


@pytest.mark.asyncio
async def test_rain_today_fires_when_forecast_has_rain():
    forecast_payload = {
        "city": {"name": "Lima", "timezone": -18000},
        "list": [
            {
                "dt": TODAY_TS,
                "main": {"temp": 17.0},
                "weather": [{"main": "Rain", "description": "lluvia ligera"}],
                "rain": {"3h": 1.4},
            }
        ],
    }
    src = _make_source_with_payload(forecast_payload)

    should_fire, ctx = await src.check(
        {"location": "Lima, PE", "condition": "rain_today", "api_key": "stub"},
        recipe_name="test",
    )

    assert should_fire is True
    assert ctx["location"] == "Lima"
    assert ctx["description"] == "lluvia ligera"
    assert ctx["precipitation_mm"] == 1.4


@pytest.mark.asyncio
async def test_rain_today_does_not_fire_on_clear_forecast():
    forecast_payload = {
        "city": {"name": "Lima", "timezone": -18000},
        "list": [
            {
                "dt": TODAY_TS,
                "main": {"temp": 22.0},
                "weather": [{"main": "Clear", "description": "cielo despejado"}],
            }
        ],
    }
    src = _make_source_with_payload(forecast_payload)

    should_fire, ctx = await src.check(
        {"location": "Lima, PE", "condition": "rain_today", "api_key": "stub"},
        recipe_name="test",
    )

    assert should_fire is False
    assert ctx["precipitation_mm"] == 0.0


@pytest.mark.asyncio
async def test_temp_above_threshold_fires_when_temp_higher():
    current_payload = {
        "name": "Lima",
        "weather": [{"main": "Clouds", "description": "nublado"}],
        "main": {"temp": 28.5, "feels_like": 29.0, "humidity": 60},
    }
    src = _make_source_with_payload(current_payload)

    should_fire, ctx = await src.check(
        {"location": "Lima, PE", "condition": "temp_above:25", "api_key": "stub"},
        recipe_name="test",
    )

    assert should_fire is True
    assert ctx["temp_c"] == 28.5


@pytest.mark.asyncio
async def test_temp_above_threshold_does_not_fire_when_temp_lower():
    current_payload = {
        "name": "Lima",
        "weather": [{"main": "Clouds", "description": "nublado"}],
        "main": {"temp": 18.0, "feels_like": 17.0, "humidity": 80},
    }
    src = _make_source_with_payload(current_payload)

    should_fire, _ = await src.check(
        {"location": "Lima, PE", "condition": "temp_above:25", "api_key": "stub"},
        recipe_name="test",
    )

    assert should_fire is False


@pytest.mark.asyncio
async def test_missing_location_raises():
    src = WeatherSource()
    with pytest.raises(RuntimeError, match="location"):
        await src.check(
            {"condition": "rain_today", "api_key": "stub"}, recipe_name="test"
        )


@pytest.mark.asyncio
async def test_unsupported_condition_raises():
    src = _make_source_with_payload({"name": "Lima", "weather": [{"main": "Clear"}], "main": {"temp": 20}})
    with pytest.raises(RuntimeError, match="unsupported condition"):
        await src.check(
            {"location": "Lima, PE", "condition": "snow_tomorrow", "api_key": "stub"},
            recipe_name="test",
        )
