"""Source registry. Sources decide whether a recipe should fire and produce
a context dict that the action can template against."""
from __future__ import annotations

from server.sources.base import Source
from server.sources.github_releases import GithubReleasesSource
from server.sources.rss import RssSource
from server.sources.weather import WeatherSource

SOURCES: dict[str, Source] = {
    "weather": WeatherSource(),
    "rss": RssSource(),
    "github_releases": GithubReleasesSource(),
}

__all__ = ["SOURCES", "Source"]
