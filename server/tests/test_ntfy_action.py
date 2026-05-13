"""Tests for NtfyAction.

httpx.AsyncClient is patched so the test never hits the network.
"""
from __future__ import annotations

import pytest

from server.actions.ntfy import NtfyAction


class _StubResponse:
    def __init__(self, status_code: int = 200):
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _StubClient:
    def __init__(self, *args, **kwargs):
        self.posted_url: str | None = None
        self.posted_body: bytes | None = None
        self.posted_headers: dict[str, str] | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, content=None, headers=None):
        self.posted_url = url
        self.posted_body = content
        self.posted_headers = headers
        return _StubResponse()


@pytest.mark.asyncio
async def test_ntfy_posts_to_correct_url_and_body(monkeypatch):
    captured: dict = {}

    class _Capturing(_StubClient):
        async def post(self, url, content=None, headers=None):
            captured["url"] = url
            captured["content"] = content
            captured["headers"] = headers
            return _StubResponse()

    monkeypatch.setattr("server.actions.ntfy.httpx.AsyncClient", _Capturing)

    action = NtfyAction()
    result = await action.run(
        {
            "server": "https://ntfy.example.com",
            "topic": "my-topic",
            "message": "hola mundo",
            "title": "Aviso",
            "priority": 4,
            "tags": ["rain", "lima"],
        },
        context={},
    )

    assert captured["url"] == "https://ntfy.example.com/my-topic"
    assert captured["content"] == b"hola mundo"
    assert captured["headers"]["Title"] == "Aviso"
    assert captured["headers"]["Priority"] == "4"
    assert captured["headers"]["Tags"] == "rain,lima"
    assert result == {
        "channel": "ntfy",
        "server": "https://ntfy.example.com",
        "topic": "my-topic",
        "chars": len("hola mundo"),
    }


@pytest.mark.asyncio
async def test_ntfy_requires_topic():
    action = NtfyAction()
    with pytest.raises(RuntimeError, match="topic"):
        await action.run(
            {"server": "https://ntfy.sh", "message": "x"},
            context={},
        )


@pytest.mark.asyncio
async def test_ntfy_requires_message():
    action = NtfyAction()
    with pytest.raises(RuntimeError, match="message"):
        await action.run(
            {"server": "https://ntfy.sh", "topic": "x", "message": ""},
            context={},
        )
