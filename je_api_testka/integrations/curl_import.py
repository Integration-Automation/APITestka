"""
Convert a ``curl`` command line into an executor action dict.

Supports the most common flags: ``-X``, ``-H``, ``-d`` / ``--data``, and the
implicit GET / POST behaviour. Bash quoting is parsed via ``shlex``.
"""
from __future__ import annotations

import json
import shlex
from typing import Dict, Optional, Tuple

from je_api_testka.utils.exception.exceptions import APITesterException

CURL_TOKEN: str = "curl"


def _parse_tokens(tokens: list) -> Tuple[str, str, Dict[str, str], Optional[object]]:
    method = ""
    url = ""
    headers: Dict[str, str] = {}
    body: Optional[object] = None
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in ("-X", "--request"):
            method = tokens[index + 1].upper()
            index += 2
            continue
        if token in ("-H", "--header"):
            raw = tokens[index + 1]
            if ":" in raw:
                key, value = raw.split(":", 1)
                headers[key.strip()] = value.strip()
            index += 2
            continue
        if token in ("-d", "--data", "--data-raw"):
            raw_body = tokens[index + 1]
            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError:
                body = raw_body
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        if not url:
            url = token.strip("'\"")
        index += 1
    if not url:
        raise APITesterException("curl command did not contain a URL")
    if not method:
        method = "POST" if body is not None else "GET"
    return method, url, headers, body


def curl_to_action(curl_command: str) -> dict:
    """Return ``{"AT_test_api_method_requests": {...}}`` for the given curl line."""
    tokens = shlex.split(curl_command)
    if not tokens or tokens[0] != CURL_TOKEN:
        raise APITesterException("input does not start with 'curl'")
    method, url, headers, body = _parse_tokens(tokens)
    payload: dict = {"http_method": method.lower(), "test_url": url}
    if headers:
        payload["headers"] = headers
    if body is not None:
        if isinstance(body, (dict, list)):
            payload["json"] = body
        else:
            payload["data"] = body
    return {"AT_test_api_method_requests": payload}
