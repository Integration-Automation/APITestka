"""Tests for ``{{var}}`` template substitution."""
from __future__ import annotations

import pytest

from je_api_testka.data.template_render import render_template, render_value
from je_api_testka.data.variable_store import VariableStore
from je_api_testka.utils.exception.exceptions import APITesterException


def test_render_value_substitutes_known_var():
    store = VariableStore()
    store.set("name", "alice")
    assert render_value("hi {{name}}", store=store) == "hi alice"


def test_render_value_unknown_returns_empty():
    store = VariableStore()
    assert render_value("hi {{name}}", store=store) == "hi "


def test_render_value_strict_raises():
    store = VariableStore()
    with pytest.raises(APITesterException):
        render_value("hi {{missing}}", store=store, strict=True)


def test_render_template_walks_dicts_lists():
    store = VariableStore()
    store.set("token", "abc")
    payload = {
        "headers": {"Authorization": "Bearer {{token}}"},
        "items": ["a", "{{token}}", {"k": "{{token}}"}],
    }
    rendered = render_template(payload, store=store)
    assert rendered["headers"]["Authorization"] == "Bearer abc"
    assert rendered["items"][1] == "abc"
    assert rendered["items"][2]["k"] == "abc"
