"""
Declarative mock configuration for ``apitestka mock --config``.

One JSON file describes HTTP, WebSocket and gRPC endpoints::

    {
      "http": {"routes": [{"rule": "/health", "body": {"ok": true}}], "openapi": "spec.json"},
      "websocket": {"port": 8765, "routes": {"/chat": {"greeting": "hi", "replies": {"ping": "pong"}}}},
      "grpc": {"port": 50051, "methods": {"/shop.Catalog/Get": {"response": {"id": 1}}}}
    }

Every section is optional. HTTP routes go onto the given :class:`FlaskMockServer`;
the WebSocket and gRPC mocks start in background threads through
:mod:`protocol_mocks`. A relative ``openapi`` path is resolved against the
config file's directory.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Mapping, Optional

from je_api_testka.utils.exception.exceptions import MockServerException
from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer
from je_api_testka.utils.mock_server.protocol_mocks import (
    start_grpc_mock,
    start_websocket_mock,
    stop_grpc_mock,
    stop_websocket_mock,
)

_SECTIONS: frozenset = frozenset({"http", "websocket", "grpc"})
_ROUTE_KEYS: frozenset = frozenset({"rule", "body", "status", "methods"})


def read_mock_config(path: str) -> dict:
    """Read a mock config file; raise :class:`MockServerException` when it is not a JSON object."""
    try:
        config = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise MockServerException(f"{path}: cannot read mock config: {error!r}") from error
    if not isinstance(config, dict):
        raise MockServerException(f"{path}: a mock config must be a JSON object")
    return config


def _section(config: Mapping[str, object], name: str) -> Optional[Mapping[str, object]]:
    value = config.get(name)
    if value is not None and not isinstance(value, dict):
        raise MockServerException(f"mock config '{name}' must be an object")
    return value


def _apply_http(server: FlaskMockServer, http: Mapping[str, object], base_dir: Path) -> None:
    routes = http.get("routes", [])
    if not isinstance(routes, list):
        raise MockServerException("mock config 'http.routes' must be a list")
    for route in routes:
        if not isinstance(route, dict) or "rule" not in route or set(route) - _ROUTE_KEYS:
            raise MockServerException(f"bad http route {route!r}; keys: rule, body, status, methods")
        server.add_template_route(route["rule"], route.get("body", ""), status=route.get("status", 200),
                                  methods=route.get("methods"))
    if "openapi" in http:
        spec_path = base_dir / str(http["openapi"])
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise MockServerException(f"{spec_path}: cannot read OpenAPI document: {error!r}") from error
        server.load_openapi(spec)


def _address(section: Mapping[str, object]) -> dict:
    return {key: section[key] for key in ("host", "port") if key in section}


def _start_protocol_mocks(config: Mapping[str, object]) -> Dict[str, str]:
    websocket = _section(config, "websocket")
    grpc = _section(config, "grpc")
    endpoints: Dict[str, str] = {}
    if websocket is not None:
        endpoints["websocket"] = start_websocket_mock(websocket.get("routes"), **_address(websocket))
    if grpc is not None:
        try:
            endpoints["grpc"] = start_grpc_mock(grpc.get("methods") or {}, **_address(grpc))
        except Exception:
            if "websocket" in endpoints:
                stop_websocket_mock()
            raise
    return endpoints


def apply_mock_config(config: Mapping[str, object], http_server: FlaskMockServer,
                      base_dir: str = ".") -> Dict[str, str]:
    """
    Register the config's HTTP routes on ``http_server`` and start its WebSocket and gRPC mocks.

    :return: the started endpoints, e.g. ``{"websocket": "ws://127.0.0.1:8765", "grpc": "127.0.0.1:50051"}``.
    :raises MockServerException: on an unknown section or a malformed entry. A WebSocket mock
        started by this call is stopped again when the gRPC mock then fails.
    """
    unknown = set(config) - _SECTIONS
    if unknown:
        raise MockServerException(f"unknown mock config sections: {sorted(unknown)}")
    http = _section(config, "http")
    if http is not None:
        _apply_http(http_server, http, Path(base_dir))
    return _start_protocol_mocks(config)


def stop_protocol_mocks() -> None:
    """Stop the WebSocket and gRPC mocks started from a config, if any."""
    stop_websocket_mock()
    stop_grpc_mock()
