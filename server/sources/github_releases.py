"""GitHub releases source. Fires when a tracked repo publishes a new release."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from server import settings_service
from server.config import settings
from server.db.connection import get_session
from server.db.schema import SourceState
from server.sources.base import Source

_STATE_KEY = "last_release_tag"


class GithubReleasesSource(Source):
    name = "github_releases"

    async def check(
        self,
        config: dict[str, Any],
        *,
        recipe_name: str,
    ) -> tuple[bool, dict[str, Any]]:
        repo = config.get("repo")
        if not repo or "/" not in repo:
            raise RuntimeError("github_releases requires 'repo' in 'owner/name' form")

        include_prereleases = bool(config.get("include_prereleases", False))
        token = settings_service.resolve(
            "github.token",
            recipe_override=config.get("token"),
            env_fallback=settings.github_token or None,
        )

        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"https://api.github.com/repos/{repo}/releases",
                headers=headers,
                params={"per_page": 10},
            )
            resp.raise_for_status()
            releases = resp.json()

        if not isinstance(releases, list) or not releases:
            return False, {"repo": repo, "count": 0}

        for release in releases:
            if release.get("prerelease") and not include_prereleases:
                continue
            if release.get("draft"):
                continue
            latest = release
            break
        else:
            return False, {"repo": repo, "count": 0}

        tag = latest.get("tag_name", "")
        last_seen = _load_last_seen(recipe_name)

        if last_seen == tag:
            return False, {"repo": repo, "latest_tag": tag}

        _store_last_seen(recipe_name, tag)

        return True, {
            "repo": repo,
            "tag": tag,
            "name": latest.get("name", ""),
            "url": latest.get("html_url", ""),
            "body": latest.get("body", ""),
            "author": (latest.get("author") or {}).get("login", ""),
            "published_at": latest.get("published_at", ""),
            "is_first_run": last_seen is None,
        }


def _load_last_seen(recipe_name: str) -> str | None:
    with get_session() as session:
        row = session.get(SourceState, (recipe_name, _STATE_KEY))
        if row is None:
            return None
        return row.value.get("tag")


def _store_last_seen(recipe_name: str, tag: str) -> None:
    with get_session() as session:
        existing = session.get(SourceState, (recipe_name, _STATE_KEY))
        if existing:
            existing.value = {"tag": tag}
            existing.updated_at = datetime.now(timezone.utc)
        else:
            session.add(
                SourceState(
                    recipe_name=recipe_name,
                    key=_STATE_KEY,
                    value={"tag": tag},
                    updated_at=datetime.now(timezone.utc),
                )
            )
