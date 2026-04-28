"""
Build mock endpoints from an OpenAPI 3.x document.

For each operation we create a Flask view that returns the first ``example`` or
``examples`` payload found in the response definition. Path parameters are
mapped from OpenAPI's ``{name}`` syntax to Flask's ``<name>``.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from flask import Response

from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_RESPONSE_BODY: str = ""
DEFAULT_RESPONSE_STATUS: int = 200
HTTP_VERBS: Tuple[str, ...] = ("get", "put", "post", "patch", "delete", "options", "head")


def _extract_example(operation: dict) -> Tuple[Any, int, str]:
    responses = operation.get("responses") or {}
    for status_str, response_def in responses.items():
        try:
            status = int(status_str)
        except (TypeError, ValueError):
            continue
        content = (response_def or {}).get("content") or {}
        for media_type, media_def in content.items():
            example = media_def.get("example")
            if example is None and media_def.get("examples"):
                first_key = next(iter(media_def["examples"]))
                example = media_def["examples"][first_key].get("value")
            if example is not None:
                return example, status, media_type
    return DEFAULT_RESPONSE_BODY, DEFAULT_RESPONSE_STATUS, "text/plain"


def _convert_path(openapi_path: str) -> str:
    return openapi_path.replace("{", "<").replace("}", ">")


def _build_view(example: Any, status: int, media_type: str):
    def _view(**_kwargs):
        if isinstance(example, (dict, list)):
            return Response(json.dumps(example), status=status, mimetype="application/json")
        return Response(str(example), status=status, mimetype=media_type)

    return _view


def register_openapi_routes(server, spec: dict) -> Dict[str, str]:
    """Register routes defined by ``spec`` on a :class:`FlaskMockServer`-like object."""
    apitestka_logger.info("openapi_loader register_openapi_routes")
    registered: Dict[str, str] = {}
    for path, item in (spec.get("paths") or {}).items():
        flask_path = _convert_path(path)
        for verb in HTTP_VERBS:
            operation = item.get(verb)
            if not operation:
                continue
            example, status, media_type = _extract_example(operation)
            view = _build_view(example, status, media_type)
            view.__name__ = f"openapi_{verb}_{flask_path.replace('/', '_').strip('_')}"
            server.app.route(flask_path, methods=[verb.upper()])(view)
            registered[f"{verb.upper()} {flask_path}"] = view.__name__
    return registered
