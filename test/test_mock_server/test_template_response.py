"""Tests for the templated mock response view."""
from __future__ import annotations

from flask import Flask

from je_api_testka.data.variable_store import variable_store
from je_api_testka.utils.mock_server.template_response import make_template_view


def test_template_view_renders_global_variable():
    variable_store.clear()
    variable_store.set("greeting", "hello")
    app = Flask(__name__)
    app.add_url_rule("/x", "x", make_template_view({"msg": "{{greeting}}"}))
    client = app.test_client()
    rsp = client.get("/x")
    assert rsp.get_json() == {"msg": "hello"}
    variable_store.clear()


def test_template_view_uses_request_json():
    variable_store.clear()
    app = Flask(__name__)
    app.add_url_rule(
        "/echo", "echo",
        make_template_view({"name": "{{request.json.name}}"}),
        methods=["POST"],
    )
    client = app.test_client()
    rsp = client.post("/echo", json={"name": "alice"})
    assert rsp.get_json() == {"name": "alice"}
    variable_store.clear()
