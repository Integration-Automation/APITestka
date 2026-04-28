"""
Convert a HAR file (HTTP Archive) into a list of executor actions.

HARs are produced by browser DevTools and many proxies; converting them gives
you a fast way to bootstrap a regression suite from real traffic.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


def convert_har(file_path: str) -> List[dict]:
    """Return a list of action dicts parsed from a HAR JSON document."""
    document = json.loads(Path(file_path).read_text(encoding="utf-8"))
    actions: List[dict] = []
    entries = (document.get("log") or {}).get("entries") or []
    for entry in entries:
        request = entry.get("request") or {}
        method = request.get("method", "GET")
        url = request.get("url")
        if not url:
            continue
        headers = {item["name"]: item["value"] for item in request.get("headers", [])
                   if "name" in item and "value" in item}
        body_value = None
        post_data = request.get("postData") or {}
        text = post_data.get("text")
        if text:
            try:
                body_value = json.loads(text)
            except json.JSONDecodeError:
                body_value = text
        payload: dict = {"http_method": method.lower(), "test_url": url}
        if headers:
            payload["headers"] = headers
        if isinstance(body_value, (dict, list)):
            payload["json"] = body_value
        elif body_value is not None:
            payload["data"] = body_value
        actions.append({"AT_test_api_method_requests": payload})
    return actions
