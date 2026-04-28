"""
Jinja-style templating for mock responses.

We avoid an extra Jinja2 dependency by reusing the project's existing
``{{var}}`` template renderer. Tokens reference variables stored in the
global VariableStore plus a few request-derived helpers.
"""
from __future__ import annotations

import json
from typing import Any

from flask import Response, request

from je_api_testka.data.template_render import render_template
from je_api_testka.data.variable_store import variable_store

DEFAULT_TEMPLATE_STATUS: int = 200


def _populate_request_variables() -> dict:
    payload = {}
    payload["request.method"] = request.method
    payload["request.path"] = request.path
    body = request.get_json(silent=True) or {}
    if isinstance(body, dict):
        for key, value in body.items():
            payload[f"request.json.{key}"] = value
    return payload


def make_template_view(body_template: Any, status: int = DEFAULT_TEMPLATE_STATUS):
    """Return a Flask view that renders ``body_template`` against the global VariableStore."""

    def _view(**_kwargs):
        for key, value in _populate_request_variables().items():
            variable_store.set(key, value)
        rendered = render_template(body_template, store=variable_store)
        if isinstance(rendered, (dict, list)):
            return Response(json.dumps(rendered), status=status, mimetype="application/json")
        return Response(str(rendered), status=status)

    _view.__name__ = "template_view"
    return _view
