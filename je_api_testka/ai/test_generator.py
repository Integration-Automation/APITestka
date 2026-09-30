"""
Generate executor action JSON from an OpenAPI spec via the active AI backend.

If the backend is :class:`NoOpAIBackend`, or its reply is empty, not JSON or
not a list of well-formed ``AT_*`` actions, we fall back to a deterministic
approach: one happy-path action per operation.
"""
from __future__ import annotations

import json
from typing import Any, List

from je_api_testka.ai.backend import NoOpAIBackend, ai_backend
from je_api_testka.ai.reply import parse_json_reply
from je_api_testka.utils.executor.request_action import REQUEST_COMMAND, build_request_action
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

HTTP_VERBS = ("get", "put", "post", "patch", "delete", "options", "head")
COMMAND_PREFIX: str = "AT_"
_ACTION_LENGTH: int = 2  # [command, kwargs or args]

TEST_GENERATION_PROMPT: str = (
    "Write APITestka test actions for the OpenAPI document in the context. Reply with a JSON array; "
    f'each element is one action of the form ["{REQUEST_COMMAND}", {{...}}] whose object takes: '
    '"http_method" (lower-case verb), "test_url" (first server URL + path, with example values in place '
    'of path parameters), optional "params" (query parameters), "headers", "json" (request body) and '
    '"result_check_dict" (e.g. {"status_code": 200}; APITestka only records 2xx and 3xx responses as '
    "successes). Cover every operation with a realistic happy-path call that uses the documented examples "
    "and required fields."
)


def _deterministic_actions(spec: dict) -> List[list]:
    actions: List[list] = []
    base = ""
    servers = spec.get("servers") or []
    if servers:
        base = servers[0].get("url", "")
    for path, item in (spec.get("paths") or {}).items():
        for verb in HTTP_VERBS:
            if not (item or {}).get(verb):
                continue
            actions.append(build_request_action(verb, f"{base}{path}", result_check_dict={"status_code": 200}))
    return actions


def _is_action(value: Any) -> bool:
    if not isinstance(value, list) or not value or len(value) > _ACTION_LENGTH:
        return False
    name = value[0]
    if not isinstance(name, str) or not name.startswith(COMMAND_PREFIX):
        return False
    return len(value) == 1 or isinstance(value[1], (dict, list))


def generate_tests_from_openapi(spec: dict) -> List[Any]:
    """
    Return executor actions via the AI backend if configured, otherwise a deterministic fallback.

    The fallback is one ``["AT_test_api_method", {...}]`` happy-path action per operation.
    A backend reply is used only when it is a non-empty JSON list of ``["AT_...", {...}]`` actions.
    """
    backend = ai_backend()
    if isinstance(backend, NoOpAIBackend):
        return _deterministic_actions(spec)
    response = backend.complete(TEST_GENERATION_PROMPT, context={"openapi": spec})
    if not response:
        return _deterministic_actions(spec)
    try:
        parsed: Any = parse_json_reply(response)
    except json.JSONDecodeError:
        apitestka_logger.error("AI backend returned non-JSON; falling back")
        return _deterministic_actions(spec)
    if isinstance(parsed, list) and parsed and all(_is_action(action) for action in parsed):
        return parsed
    apitestka_logger.error("AI backend reply is not a list of AT_* actions; falling back")
    return _deterministic_actions(spec)
