"""
Reconstruct an OpenAPI 3.x dictionary from the global test record.

This is a coarse, "good enough to start" approach: it groups records by
(method, path), keeps one response entry per status code, and infers
response and request-body schemas via :func:`infer_schema`. Query parameter
names seen in the URLs become ``in: query`` parameters. Path templating is
not detected automatically.
"""
from __future__ import annotations

import json
from typing import Any, Iterable, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

from je_api_testka.spec.schema_inference import infer_schema
from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_OPENAPI_VERSION: str = "3.1.0"
DEFAULT_SPEC_TITLE: str = "APITestka Inferred"
DEFAULT_SPEC_VERSION: str = "0.1.0"
JSON_MEDIA_TYPE: str = "application/json"
TEXT_MEDIA_TYPE: str = "text/plain"


def decode_body(raw: Any) -> Optional[Tuple[str, Any]]:
    """
    Return ``(media type, value)`` for a recorded body, or ``None`` when it is empty or not UTF-8.

    JSON text becomes ``("application/json", parsed value)``; any other text ``("text/plain", text)``.
    """
    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError:
            return None
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return JSON_MEDIA_TYPE, json.loads(raw)
    except json.JSONDecodeError:
        return TEXT_MEDIA_TYPE, raw


def _content(raw: Any) -> Optional[dict]:
    """Return an OpenAPI ``content`` map for a body, or ``None`` when it is empty."""
    sample = decode_body(raw)
    if sample is None:
        return None
    media_type, value = sample
    return {media_type: {"schema": infer_schema(value)}}


def _response_entry(record: dict) -> dict:
    entry: dict = {"description": "inferred"}
    content = _content(record.get("text"))
    if content is not None:
        entry["content"] = content
    return entry


def _merge_query_parameters(operation: dict, query: str) -> None:
    """Add a ``query`` parameter for each name in ``query`` the operation does not list yet."""
    parameters = operation.setdefault("parameters", [])
    known = {parameter["name"] for parameter in parameters}
    for name, _value in parse_qsl(query, keep_blank_values=True):
        if name not in known:
            parameters.append({"name": name, "in": "query", "schema": {"type": "string"}})
            known.add(name)
    if not parameters:
        del operation["parameters"]


def _add_record(paths: dict, record: dict) -> None:
    url = record.get("request_url") or ""
    if not url:
        return
    parsed = urlparse(url)
    method = (record.get("request_method") or "get").lower()
    operation = paths.setdefault(parsed.path or "/", {}).setdefault(method, {"responses": {}})
    operation["responses"][str(record.get("status_code", 200))] = _response_entry(record)
    _merge_query_parameters(operation, parsed.query)
    request_content = _content(record.get("request_body"))
    if request_content is not None:
        operation["requestBody"] = {"content": request_content}


def records_to_openapi(records: Optional[Iterable[dict]] = None, title: str = DEFAULT_SPEC_TITLE,
                       version: str = DEFAULT_SPEC_VERSION) -> dict:
    """
    Return an OpenAPI 3.x dictionary describing the supplied (or global) records.

    Records for the same method and path merge into one operation: each status
    code keeps the latest response seen, and query parameter names accumulate.
    """
    source = list(records) if records is not None else list(test_record_instance.test_record_list)
    paths: dict = {}
    for record in source:
        _add_record(paths, record)
    return {
        "openapi": DEFAULT_OPENAPI_VERSION,
        "info": {"title": title, "version": version},
        "paths": paths,
    }
