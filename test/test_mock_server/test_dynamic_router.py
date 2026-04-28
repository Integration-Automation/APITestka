"""Tests for the dynamic router used by the Flask mock server."""
from __future__ import annotations

from flask import Flask

from je_api_testka.utils.mock_server.dynamic_router import (
    DynamicRouter,
    json_match,
    static_response,
)


def _client_with(router: DynamicRouter):
    # In-process Flask test client; no real network exposure, no form auth
    # surface, so CSRF protection is intentionally not configured.
    app = Flask(__name__)  # NOSONAR S4502
    app.add_url_rule("/echo", "echo", router.dispatch, methods=["POST"])
    return app.test_client()


def test_first_matching_rule_wins():
    router = DynamicRouter()
    router.add(
        json_match("type", "ping"),
        static_response({"pong": True}),
        name="ping",
    )
    router.add(
        json_match("type", "shout"),
        static_response("LOUD", status=418),
        name="shout",
    )
    client = _client_with(router)
    rsp = client.post("/echo", json={"type": "ping"})
    assert rsp.status_code == 200
    assert rsp.get_json() == {"pong": True}


def test_fallthrough_returns_default_status():
    router = DynamicRouter(fallthrough_status=404, fallthrough_body="no match")
    client = _client_with(router)
    rsp = client.post("/echo", json={"type": "?"})
    assert rsp.status_code == 404
    assert rsp.data.decode() == "no match"


def test_static_response_can_set_headers():
    router = DynamicRouter()
    router.add(
        lambda req: True,
        static_response("ok", status=200, headers={"X-Mock": "1"}),
    )
    client = _client_with(router)
    rsp = client.post("/echo", json={})
    assert rsp.headers["X-Mock"] == "1"
