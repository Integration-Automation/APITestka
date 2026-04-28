"""
OpenAPI 3.x and Postman 2.1 collection importers.

Both functions return a list of action dictionaries usable with the existing
JSON-driven executor (``execute_action``).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

UNSUPPORTED_SPEC_FORMAT: str = "Unsupported spec format. Choose 'openapi' or 'postman'."
HTTP_VERBS: tuple = ("get", "put", "post", "patch", "delete", "options", "head")


def _action_for_request(method: str, url: str, headers: dict = None, body: dict = None) -> dict:
    payload = {
        "AT_test_api_method_requests": {
            "http_method": method.lower(),
            "test_url": url,
        }
    }
    if headers:
        payload["AT_test_api_method_requests"]["headers"] = headers
    if body is not None:
        payload["AT_test_api_method_requests"]["json"] = body
    return payload


def convert_openapi(spec: dict, base_url: str = "") -> List[dict]:
    """Convert an OpenAPI 3.x dict into a list of executor action dicts."""
    apitestka_logger.info("import_specs convert_openapi")
    if not base_url:
        servers = spec.get("servers") or []
        base_url = servers[0].get("url", "") if servers else ""
    actions: List[dict] = []
    for path, item in (spec.get("paths") or {}).items():
        for verb in HTTP_VERBS:
            operation = item.get(verb)
            if not operation:
                continue
            actions.append(_action_for_request(verb, f"{base_url}{path}"))
    return actions


def _iterate_postman_items(items: Iterable[dict]) -> Iterable[dict]:
    for entry in items:
        if "item" in entry:
            yield from _iterate_postman_items(entry["item"])
        elif "request" in entry:
            yield entry


def convert_postman(collection: dict) -> List[dict]:
    """Convert a Postman 2.1 collection dict into action dicts."""
    apitestka_logger.info("import_specs convert_postman")
    actions: List[dict] = []
    for entry in _iterate_postman_items(collection.get("item") or []):
        request = entry["request"]
        method = request.get("method", "GET")
        url_field = request.get("url")
        url = url_field.get("raw") if isinstance(url_field, dict) else url_field
        if not url:
            continue
        headers = {h["key"]: h["value"] for h in request.get("header", []) if "key" in h}
        body = None
        body_field = request.get("body") or {}
        if body_field.get("mode") == "raw" and body_field.get("raw"):
            try:
                body = json.loads(body_field["raw"])
            except json.JSONDecodeError:
                body = body_field["raw"]
        actions.append(_action_for_request(method, url, headers=headers or None, body=body))
    return actions


def convert_spec_file(input_path: str, spec_format: str) -> List[dict]:
    """Read ``input_path`` and dispatch to the matching converter."""
    text = Path(input_path).read_text(encoding="utf-8")
    document = json.loads(text)
    if spec_format == "openapi":
        return convert_openapi(document)
    if spec_format == "postman":
        return convert_postman(document)
    raise APITesterException(UNSUPPORTED_SPEC_FORMAT)
