"""Tests for chat-platform notifications."""
from __future__ import annotations

import json

import httpx
import pytest

from je_api_testka.integrations.notify import (
    DISCORD_PLATFORM,
    SLACK_PLATFORM,
    TEAMS_PLATFORM,
    notify_via_webhook,
)
from je_api_testka.utils.exception.exceptions import APITesterException


def _capture_transport():
    captured = {}

    def _handler(request):
        captured["url"] = str(request.url)
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, text="ok")

    return captured, httpx.MockTransport(_handler)


def test_slack_payload_uses_text_field():
    captured, transport = _capture_transport()
    status = notify_via_webhook("https://hooks.invalid/x", "hello", platform=SLACK_PLATFORM,
                                transport=transport)
    assert status == 200
    assert captured["payload"] == {"text": "hello"}


def test_discord_payload_uses_content_field():
    captured, transport = _capture_transport()
    notify_via_webhook("https://discord.invalid/x", "hi", platform=DISCORD_PLATFORM,
                       transport=transport)
    assert captured["payload"] == {"content": "hi"}


def test_teams_payload_uses_text_field():
    captured, transport = _capture_transport()
    notify_via_webhook("https://teams.invalid/x", "msg", platform=TEAMS_PLATFORM,
                       transport=transport)
    assert captured["payload"] == {"text": "msg"}


def test_unsupported_platform_raises():
    _, transport = _capture_transport()
    with pytest.raises(APITesterException):
        notify_via_webhook("https://x.invalid", "hi", platform="myspace", transport=transport)
