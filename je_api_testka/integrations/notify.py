"""
Outbound notifications to chat platforms.

Slack, Microsoft Teams, and Discord all accept incoming-webhook POSTs whose
body is a JSON object with a ``text``-like field. We accept a webhook URL and
a markdown summary, then dispatch with the right schema for the platform.
"""
from __future__ import annotations

import json
from typing import Optional

import httpx

from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_NOTIFY_TIMEOUT_SECONDS: float = 10.0
SLACK_PLATFORM: str = "slack"
TEAMS_PLATFORM: str = "teams"
DISCORD_PLATFORM: str = "discord"
SUPPORTED_PLATFORMS = (SLACK_PLATFORM, TEAMS_PLATFORM, DISCORD_PLATFORM)


def _build_payload(platform: str, summary: str) -> dict:
    if platform == SLACK_PLATFORM:
        return {"text": summary}
    if platform == DISCORD_PLATFORM:
        return {"content": summary}
    if platform == TEAMS_PLATFORM:
        return {"text": summary}
    raise APITesterException(f"unsupported platform {platform}; expected one of {SUPPORTED_PLATFORMS}")


def notify_via_webhook(
    webhook_url: str,
    summary: str,
    platform: str = SLACK_PLATFORM,
    timeout: float = DEFAULT_NOTIFY_TIMEOUT_SECONDS,
    transport: Optional[object] = None,
) -> int:
    """POST a markdown summary to a chat-platform incoming webhook. Returns status code."""
    apitestka_logger.info(f"notify notify_via_webhook platform: {platform}")
    payload = _build_payload(platform, summary)
    client_kwargs = {"timeout": timeout}
    if transport is not None:
        client_kwargs["transport"] = transport
    with httpx.Client(**client_kwargs) as client:
        response = client.post(
            webhook_url,
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
    return response.status_code
