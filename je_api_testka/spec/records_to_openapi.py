"""
Reconstruct an OpenAPI 3.x dictionary from the global test record.

This is a coarse, "good enough to start" approach: it groups records by
(method, path) and infers response schemas via :func:`infer_schema`. Path
templating is not detected automatically.
"""
from __future__ import annotations

import json
from typing import Iterable
from urllib.parse import urlparse

from je_api_testka.spec.schema_inference import infer_schema
from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_OPENAPI_VERSION: str = "3.1.0"


def _decode_body(record: dict):
    text = record.get("text") or ""
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def records_to_openapi(records: Iterable[dict] = None, title: str = "APITestka Inferred",
                       version: str = "0.1.0") -> dict:
    """Return an OpenAPI 3.x dictionary describing the supplied (or global) records."""
    source = list(records) if records is not None else list(test_record_instance.test_record_list)
    paths: dict = {}
    for record in source:
        url = record.get("request_url") or ""
        method = (record.get("request_method") or "get").lower()
        if not url:
            continue
        parsed = urlparse(url)
        path = parsed.path or "/"
        body = _decode_body(record)
        operation = {
            "responses": {
                str(record.get("status_code", 200)): {
                    "description": "inferred",
                    "content": {
                        "application/json": {"schema": infer_schema(body)} if body is not None else {"text/plain": {}}
                    },
                }
            }
        }
        paths.setdefault(path, {})[method] = operation
    return {
        "openapi": DEFAULT_OPENAPI_VERSION,
        "info": {"title": title, "version": version},
        "paths": paths,
    }
