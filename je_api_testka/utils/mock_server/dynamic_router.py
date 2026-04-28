"""
Conditional response routing for the Flask mock server.

Each rule is a callable taking the Flask ``request`` and returning either a
``(body, status, headers)`` tuple or ``None`` to fall through to the next rule.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple

from flask import Response, request

from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_FALLTHROUGH_STATUS: int = 404
DEFAULT_FALLTHROUGH_BODY: str = "no matching dynamic rule"
DEFAULT_OK_STATUS: int = 200

ResponseTuple = Tuple[Any, int, Optional[dict]]
RuleCallable = Callable[[Any], Optional[ResponseTuple]]


@dataclass
class DynamicRule:
    """Pair an arbitrary predicate with a response builder."""

    predicate: Callable[[Any], bool]
    responder: Callable[[Any], ResponseTuple]
    name: str = ""


@dataclass
class DynamicRouter:
    """Stateless registry of :class:`DynamicRule` objects, evaluated in order."""

    rules: List[DynamicRule] = field(default_factory=list)
    fallthrough_status: int = DEFAULT_FALLTHROUGH_STATUS
    fallthrough_body: str = DEFAULT_FALLTHROUGH_BODY

    def add(self, predicate: Callable[[Any], bool],
            responder: Callable[[Any], ResponseTuple], name: str = "") -> None:
        self.rules.append(DynamicRule(predicate=predicate, responder=responder, name=name))

    def dispatch(self) -> Response:
        for rule in self.rules:
            try:
                if rule.predicate(request):
                    body, status, headers = rule.responder(request)
                    return _make_response(body, status, headers)
            except (TypeError, ValueError) as error:
                apitestka_logger.error(
                    f"DynamicRouter rule '{rule.name}' failed: {repr(error)}"
                )
        return _make_response(self.fallthrough_body, self.fallthrough_status, None)


def _make_response(body: Any, status: int, headers: Optional[dict]) -> Response:
    if isinstance(body, (dict, list)):
        response = Response(json.dumps(body), status=status, mimetype="application/json")
    else:
        response = Response(str(body), status=status)
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response


def json_match(field_path: str, expected: Any) -> Callable[[Any], bool]:
    """Predicate that compares ``request.json[field_path]`` (dotted) against ``expected``."""

    def _predicate(req) -> bool:
        payload = req.get_json(silent=True) or {}
        cursor: Any = payload
        for piece in field_path.split("."):
            if isinstance(cursor, dict) and piece in cursor:
                cursor = cursor[piece]
            else:
                return False
        return cursor == expected

    return _predicate


def static_response(body: Any, status: int = DEFAULT_OK_STATUS,
                    headers: Optional[dict] = None) -> Callable[[Any], ResponseTuple]:
    """Helper to return the same response regardless of the request."""

    def _responder(_req) -> ResponseTuple:
        return body, status, headers

    return _responder
