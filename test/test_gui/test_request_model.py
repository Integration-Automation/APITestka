"""Tests for the Qt-free model behind the request page, and the theme style sheets."""
from __future__ import annotations

import pytest

from je_api_testka.data.variable_store import variable_store
from je_api_testka.gui.request_model import (
    RequestSpec,
    describe_response,
    parse_body,
    parse_json_field,
    send_request,
)
from je_api_testka.gui.theme import THEMES, build_stylesheet, resolve_theme
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def test_parse_json_field():
    assert parse_json_field("  ", "Params") is None
    assert parse_json_field('{"a": 1}', "Params") == {"a": 1}
    with pytest.raises(ValueError, match="Params: not valid JSON"):
        parse_json_field("{a", "Params")


def test_parse_body_keeps_text():
    assert parse_body("") is None
    assert parse_body('[1, 2]') == [1, 2]
    assert parse_body("plain") == "plain"


@pytest.mark.parametrize("backend", ["requests", "httpx", "httpx_async"])
def test_send_request_renders_environment_variables(mock_url, backend):
    variable_store.set("base", mock_url)
    variable_store.set("page", "3")
    try:
        data = send_request(RequestSpec(method="get", url="{{base}}/get", backend=backend,
                                        params={"page": "{{page}}"}, headers={"X-Test": "1"}))
    finally:
        variable_store.clear()
    view = describe_response(data)
    assert (view.status, view.status_class) == (200, "success")
    assert '"page": "3"' in view.body
    assert "content-type" in view.headers.lower()
    assert view.size_bytes > 0 and view.elapsed_ms >= 0


def test_send_request_json_body_and_auth(mock_url):
    data = send_request(RequestSpec(method="post", url=f"{mock_url}/post", backend="requests",
                                    body={"a": 1}, auth={"username": "u", "password": "p"}))
    assert '"method": "POST"' in describe_response(data).body


def test_send_request_errors(mock_url):
    with pytest.raises(APITesterException, match="URL is empty"):
        send_request(RequestSpec(method="get", url="  "))
    with pytest.raises(APITesterException, match="unknown backend"):
        send_request(RequestSpec(method="get", url=f"{mock_url}/get", backend="curl"))
    with pytest.raises(APITesterException, match="request failed"):
        send_request(RequestSpec(method="get", url=f"{mock_url}/missing", backend="requests"))
    assert test_record_instance.error_record_list


@pytest.mark.parametrize(("status", "status_class"), [(204, "success"), (302, "redirect"), (404, "client-error"),
                                                      (503, "server-error")])
def test_describe_response_status_classes(status, status_class):
    view = describe_response({"status_code": status, "text": "not json", "headers": {"A": "b"}, "content": b"xy"})
    assert (view.status_class, view.body, view.headers, view.size_bytes) == (status_class, "not json", "A: b", 2)


def test_stylesheets():
    for name, palette in THEMES.items():
        sheet = build_stylesheet(name)
        assert palette.accent in sheet and palette.window in sheet
        assert "QListWidget#sidebar" in sheet
    with pytest.raises(ValueError):
        build_stylesheet("sepia")
    assert resolve_theme("dark") == "dark"
