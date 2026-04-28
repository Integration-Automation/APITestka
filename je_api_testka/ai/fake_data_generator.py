"""
Generate a payload that satisfies a JSON Schema.

If a real AI backend is configured, we ask it. Otherwise we deterministically
fill in primitives based on schema ``type``.
"""
from __future__ import annotations

import json
from typing import Any

from je_api_testka.ai.backend import NoOpAIBackend, ai_backend
from je_api_testka.data.faker_helpers import fake_email, fake_uuid, fake_word
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def _deterministic(schema: dict) -> Any:
    schema_type = schema.get("type")
    if schema_type == "object":
        return {key: _deterministic(value) for key, value in (schema.get("properties") or {}).items()}
    if schema_type == "array":
        return [_deterministic(schema.get("items") or {})]
    if schema_type == "integer":
        return 1
    if schema_type == "number":
        return 1.0
    if schema_type == "boolean":
        return True
    if schema_type == "null":
        return None
    fmt = schema.get("format", "")
    if fmt == "uuid":
        return fake_uuid()
    if fmt == "email":
        return fake_email()
    return fake_word()


def generate_fake_payload(schema: dict) -> Any:
    """Return a payload that conforms to ``schema``."""
    backend = ai_backend()
    if isinstance(backend, NoOpAIBackend):
        return _deterministic(schema)
    response = backend.complete(
        "Produce a JSON value that satisfies this schema.",
        context={"schema": schema},
    )
    if not response:
        return _deterministic(schema)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        apitestka_logger.error("AI backend returned non-JSON for fake payload; falling back")
        return _deterministic(schema)
