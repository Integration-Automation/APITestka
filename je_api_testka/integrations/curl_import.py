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
_METHOD_FLAGS = ("-X", "--request")
_HEADER_FLAGS = ("-H", "--header")
_DATA_FLAGS = ("-d", "--data", "--data-raw")


def _parse_header(raw: str) -> Optional[Tuple[str, str]]:
    if ":" not in raw:
        return None
    key, value = raw.split(":", 1)
    return key.strip(), value.strip()


def _parse_body(raw: str) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _consume_token(token: str, value: Optional[str], state: dict) -> int:
    """Apply one token to ``state``. Returns how many tokens to advance."""
    if token in _METHOD_FLAGS:
        state["method"] = (value or "").upper()
        return 2
    if token in _HEADER_FLAGS:
        parsed = _parse_header(value or "")
        if parsed is not None:
            state["headers"][parsed[0]] = parsed[1]
        return 2
    if token in _DATA_FLAGS:
        state["body"] = _parse_body(value or "")
        return 2
    if token.startswith("-"):
        return 1
    if not state["url"]:
        state["url"] = token.strip("'\"")
    return 1


def _parse_tokens(tokens: list) -> Tuple[str, str, Dict[str, str], Optional[object]]:
    state: dict = {"method": "", "url": "", "headers": {}, "body": None}
    index = 1
    while index < len(tokens):
        token = tokens[index]
        next_value = tokens[index + 1] if index + 1 < len(tokens) else None
        index += _consume_token(token, next_value, state)
    if not state["url"]:
        raise APITesterException("curl command did not contain a URL")
    method = state["method"] or ("POST" if state["body"] is not None else "GET")
    return method, state["url"], state["headers"], state["body"]


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
        payload["json" if isinstance(body, (dict, list)) else "data"] = body
    return {"AT_test_api_method_requests": payload}
