"""
OpenAPI 3.x and Postman 2.1 collection importers.

Both functions return a list of ``["AT_test_api_method", {...}]`` actions that
``execute_action`` runs as they are.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.executor.request_action import build_request_action
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

UNSUPPORTED_SPEC_FORMAT: str = "Unsupported spec format. Choose 'openapi' or 'postman'."
HTTP_VERBS: tuple = ("get", "put", "post", "patch", "delete", "options", "head")


def convert_openapi(spec: dict, base_url: str = "") -> List[list]:
    """Convert an OpenAPI 3.x dict into a list of executor actions, one per operation."""
    apitestka_logger.info("import_specs convert_openapi")
    if not base_url:
        servers = spec.get("servers") or []
        base_url = servers[0].get("url", "") if servers else ""
    actions: List[list] = []
    for path, item in (spec.get("paths") or {}).items():
        for verb in HTTP_VERBS:
            operation = item.get(verb)
            if not operation:
                continue
            actions.append(build_request_action(verb, f"{base_url}{path}"))
    return actions


def _iterate_postman_items(items: Iterable[dict]) -> Iterable[dict]:
    for entry in items:
        if "item" in entry:
            yield from _iterate_postman_items(entry["item"])
        elif "request" in entry:
            yield entry


def convert_postman(collection: dict) -> List[list]:
    """Convert a Postman 2.1 collection dict into executor actions; a non-JSON raw body is sent as ``data``."""
    apitestka_logger.info("import_specs convert_postman")
    actions: List[list] = []
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
        actions.append(build_request_action(method, url, headers=headers, body=body))
    return actions


def convert_spec_file(input_path: str, spec_format: str) -> List[list]:
    """Read ``input_path`` and dispatch to the matching converter."""
    text = Path(input_path).read_text(encoding="utf-8")
    document = json.loads(text)
    if spec_format == "openapi":
        return convert_openapi(document)
    if spec_format == "postman":
        return convert_postman(document)
    raise APITesterException(UNSUPPORTED_SPEC_FORMAT)
