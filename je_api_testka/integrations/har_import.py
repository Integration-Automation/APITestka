"""
Convert a HAR file (HTTP Archive) into a list of executor actions.

HARs are produced by browser DevTools and many proxies; converting them gives
you a fast way to bootstrap a regression suite from real traffic.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


def _decode_text_body(text: Optional[str]) -> Optional[object]:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _build_payload(method: str, url: str, headers: dict, body_value: object) -> dict:
    payload: dict = {"http_method": method.lower(), "test_url": url}
    if headers:
        payload["headers"] = headers
    if isinstance(body_value, (dict, list)):
        payload["json"] = body_value
    elif body_value is not None:
        payload["data"] = body_value
    return payload


def _entry_to_action(entry: dict) -> Optional[dict]:
    request = entry.get("request") or {}
    url = request.get("url")
    if not url:
        return None
    method = request.get("method", "GET")
    headers = {item["name"]: item["value"]
               for item in request.get("headers", [])
               if "name" in item and "value" in item}
    body_value = _decode_text_body((request.get("postData") or {}).get("text"))
    return {"AT_test_api_method_requests": _build_payload(method, url, headers, body_value)}


def convert_har(file_path: str) -> List[dict]:
    """Return a list of action dicts parsed from a HAR JSON document."""
    document = json.loads(Path(file_path).read_text(encoding="utf-8"))
    entries = (document.get("log") or {}).get("entries") or []
    actions = [action for action in (_entry_to_action(entry) for entry in entries)
               if action is not None]
    return actions
