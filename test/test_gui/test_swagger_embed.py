"""Tests for the Swagger UI embed helper."""
from __future__ import annotations

import builtins

import pytest

from je_api_testka.gui.swagger_embed import (
    DEFAULT_SWAGGER_VERSION,
    build_swagger_html,
    build_swagger_widget,
)
from je_api_testka.utils.exception.exceptions import APITesterException


def test_build_swagger_html_embeds_url_and_version():
    html = build_swagger_html("https://example.invalid/openapi.json", version="5.0.0")
    assert "swagger-ui-dist@5.0.0" in html
    assert "https://example.invalid/openapi.json" in html


def test_build_swagger_html_default_version_present():
    html = build_swagger_html("https://example.invalid/openapi.json")
    assert DEFAULT_SWAGGER_VERSION in html


def test_build_swagger_widget_dependency_missing(monkeypatch):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name.startswith("PySide6"):
            raise ImportError("nope")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    with pytest.raises(APITesterException) as excinfo:
        build_swagger_widget("https://example.invalid/openapi.json")
    assert "PySide6" in str(excinfo.value)
