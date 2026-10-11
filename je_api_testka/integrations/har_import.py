"""
Convert a HAR file (HTTP Archive) into a list of executor actions.

HARs are produced by browser DevTools and many proxies; converting them gives
you a fast way to bootstrap a regression suite from real traffic.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from je_api_testka.utils.executor.request_action import build_request_action


def _decode_text_body(text: Optional[str]) -> Optional[object]:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _entry_to_action(entry: dict) -> Optional[list]:
    request = entry.get("request") or {}
    url = request.get("url")
    if not url:
        return None
    method = request.get("method", "GET")
    headers = {item["name"]: item["value"]
               for item in request.get("headers", [])
               if "name" in item and "value" in item}
    body_value = _decode_text_body((request.get("postData") or {}).get("text"))
    return build_request_action(method, url, headers=headers, body=body_value)


def convert_har(file_path: str) -> List[list]:
    """Return a list of executor actions parsed from a HAR JSON document."""
    document = json.loads(Path(file_path).read_text(encoding="utf-8"))
    entries = (document.get("log") or {}).get("entries") or []
    actions = [action for action in (_entry_to_action(entry) for entry in entries)
               if action is not None]
    return actions
