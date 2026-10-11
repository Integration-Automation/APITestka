"""
Generate a payload that satisfies a JSON Schema.

If a real AI backend is configured, we ask it. Otherwise we deterministically
fill in primitives based on schema ``type``.
"""
from __future__ import annotations

import json
from typing import Any

from je_api_testka.ai.backend import NoOpAIBackend, ai_backend
from je_api_testka.ai.reply import parse_json_reply
from je_api_testka.data.faker_helpers import fake_email, fake_uuid, fake_word
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

_SCALARS = {"integer": 1, "number": 1.0, "boolean": True, "null": None}
_STRING_FORMATS = {"uuid": fake_uuid, "email": fake_email}


def _deterministic(schema: dict) -> Any:
    schema_type = schema.get("type")
    if schema_type == "object":
        return {key: _deterministic(value) for key, value in (schema.get("properties") or {}).items()}
    if schema_type == "array":
        return [_deterministic(schema.get("items") or {})]
    if schema_type in _SCALARS:
        return _SCALARS[schema_type]
    return _STRING_FORMATS.get(schema.get("format", ""), fake_word)()


def generate_fake_payload(schema: dict) -> Any:
    """Return a payload that conforms to ``schema``."""
    backend = ai_backend()
    if isinstance(backend, NoOpAIBackend):
        return _deterministic(schema)
    response = backend.complete(
        "Reply with one realistic JSON value that satisfies the JSON Schema in the context.",
        context={"schema": schema},
    )
    if not response:
        return _deterministic(schema)
    try:
        return parse_json_reply(response)
    except json.JSONDecodeError:
        apitestka_logger.error("AI backend returned non-JSON for fake payload; falling back")
        return _deterministic(schema)
