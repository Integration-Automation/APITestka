"""
Generate executor action JSON from an OpenAPI spec via the active AI backend.

If the backend is :class:`NoOpAIBackend` we fall back to a deterministic
``records_to_openapi``-style approach: one happy-path action per operation.
"""
from __future__ import annotations

import json
from typing import Any, List

from je_api_testka.ai.backend import NoOpAIBackend, ai_backend
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

HTTP_VERBS = ("get", "put", "post", "patch", "delete", "options", "head")


def _deterministic_actions(spec: dict) -> List[dict]:
    actions: List[dict] = []
    base = ""
    servers = spec.get("servers") or []
    if servers:
        base = servers[0].get("url", "")
    for path, item in (spec.get("paths") or {}).items():
        for verb in HTTP_VERBS:
            if not (item or {}).get(verb):
                continue
            actions.append({
                "AT_test_api_method_requests": {
                    "http_method": verb,
                    "test_url": f"{base}{path}",
                    "result_check_dict": {"status_code": 200},
                },
            })
    return actions


def generate_tests_from_openapi(spec: dict) -> List[dict]:
    """Return action dicts via the AI backend if configured, otherwise deterministic fallback."""
    backend = ai_backend()
    if isinstance(backend, NoOpAIBackend):
        return _deterministic_actions(spec)
    response = backend.complete(
        "Generate APITestka action JSON for the following OpenAPI document.",
        context={"spec": spec},
    )
    if not response:
        return _deterministic_actions(spec)
    try:
        parsed: Any = json.loads(response)
    except json.JSONDecodeError:
        apitestka_logger.error("AI backend returned non-JSON; falling back")
        return _deterministic_actions(spec)
    if isinstance(parsed, list):
        return parsed
    return _deterministic_actions(spec)
