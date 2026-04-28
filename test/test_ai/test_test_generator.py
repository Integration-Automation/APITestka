"""Tests for AI-driven test generation with deterministic fallback."""
from __future__ import annotations

import json

from je_api_testka.ai.backend import NoOpAIBackend, StaticAIBackend, set_ai_backend
from je_api_testka.ai.test_generator import generate_tests_from_openapi


_SPEC = {
    "servers": [{"url": "https://api.invalid"}],
    "paths": {
        "/users": {
            "get": {"responses": {"200": {}}},
            "post": {"responses": {"201": {}}},
        }
    },
}


def test_noop_backend_uses_deterministic_fallback():
    set_ai_backend(NoOpAIBackend())
    actions = generate_tests_from_openapi(_SPEC)
    methods = sorted(a["AT_test_api_method_requests"]["http_method"] for a in actions)
    assert methods == ["get", "post"]


def test_real_backend_response_used_when_valid_json():
    set_ai_backend(StaticAIBackend(response=json.dumps([{"AT_test_api_method_requests": {"http_method": "head", "test_url": "x"}}])))
    actions = generate_tests_from_openapi(_SPEC)
    assert actions[0]["AT_test_api_method_requests"]["http_method"] == "head"
    set_ai_backend(NoOpAIBackend())


def test_invalid_json_falls_back():
    set_ai_backend(StaticAIBackend(response="not json"))
    actions = generate_tests_from_openapi(_SPEC)
    assert actions  # deterministic fallback ran
    set_ai_backend(NoOpAIBackend())
