"""Tests for openapi_loader.register_openapi_routes."""
from __future__ import annotations

from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer


_SPEC = {
    "paths": {
        "/users/{user_id}": {
            "get": {
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {"example": {"id": 7, "name": "alice"}}
                        }
                    }
                }
            }
        },
        "/health": {
            "get": {
                "responses": {
                    "200": {"content": {"text/plain": {"example": "ok"}}}
                }
            }
        },
    }
}


def test_register_openapi_routes_serves_examples():
    server = FlaskMockServer("127.0.0.1", 0)
    registered = server.load_openapi(_SPEC)
    assert "GET /users/<user_id>" in registered
    client = server.app.test_client()

    health = client.get("/health")
    assert health.status_code == 200
    assert health.data == b"ok"

    user = client.get("/users/7")
    assert user.status_code == 200
    assert user.get_json() == {"id": 7, "name": "alice"}
