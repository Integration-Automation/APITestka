"""Tests for AI-driven fake data with deterministic fallback."""
from __future__ import annotations

import json
import uuid

from je_api_testka.ai.backend import NoOpAIBackend, StaticAIBackend, set_ai_backend
from je_api_testka.ai.fake_data_generator import generate_fake_payload


def test_deterministic_object():
    set_ai_backend(NoOpAIBackend())
    schema = {"type": "object", "properties": {
        "id": {"type": "string", "format": "uuid"},
        "age": {"type": "integer"},
    }}
    payload = generate_fake_payload(schema)
    uuid.UUID(payload["id"])  # must parse
    assert payload["age"] == 1


def test_static_backend_returns_value_via_json():
    set_ai_backend(StaticAIBackend(response=json.dumps({"id": "ai", "age": 99})))
    payload = generate_fake_payload({"type": "object"})
    assert payload == {"id": "ai", "age": 99}
    set_ai_backend(NoOpAIBackend())


def test_invalid_json_falls_back():
    set_ai_backend(StaticAIBackend(response="not json"))
    payload = generate_fake_payload({"type": "string"})
    assert isinstance(payload, str)
    set_ai_backend(NoOpAIBackend())
