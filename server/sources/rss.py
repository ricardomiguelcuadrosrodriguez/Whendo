"""RSS / Atom feed source. Fires on entries newer than the last one seen."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import feedparser

from server.db.connection import get_session
from server.db.schema import SourceState
from server.sources.base import Source

_STATE_KEY = "last_entry_id"


class RssSource(Source):
    name = "rss"

    async def check(
        self,
        config: dict[str, Any],
        *,
        recipe_name: str,
    ) -> tuple[bool, dict[str, Any]]:
        url = config.get("url")
        if not url:
            raise RuntimeError("rss source requires 'url'")

        parsed = feedparser.parse(url)
        entries = parsed.entries or []
        if not entries:
            return False, {"feed_url": url, "entries_seen": 0}

        latest = entries[0]
        latest_id = latest.get("id") or latest.get("link") or latest.get("title", "")

        last_seen = _load_last_seen(recipe_name)
        if last_seen == latest_id:
            return False, {
                "feed_url": url,
                "feed_title": parsed.feed.get("title", ""),
                "latest_title": latest.get("title", ""),
            }

        _store_last_seen(recipe_name, latest_id)

        return True, {
            "feed_url": url,
            "feed_title": parsed.feed.get("title", ""),
            "title": latest.get("title", ""),
            "link": latest.get("link", ""),
            "summary": latest.get("summary", ""),
            "author": latest.get("author", ""),
            "published": latest.get("published", ""),
            "is_first_run": last_seen is None,
        }


def _load_last_seen(recipe_name: str) -> str | None:
    with get_session() as session:
        row = session.get(SourceState, (recipe_name, _STATE_KEY))
        if row is None:
            return None
        return row.value.get("id")


def _store_last_seen(recipe_name: str, entry_id: str) -> None:
    with get_session() as session:
        existing = session.get(SourceState, (recipe_name, _STATE_KEY))
        if existing:
            existing.value = {"id": entry_id}
            existing.updated_at = datetime.now(timezone.utc)
        else:
            session.add(
                SourceState(
                    recipe_name=recipe_name,
                    key=_STATE_KEY,
                    value={"id": entry_id},
                    updated_at=datetime.now(timezone.utc),
                )
            )
