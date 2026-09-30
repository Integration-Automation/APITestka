"""
Start and stop the WebSocket and gRPC mocks by name, for JSON actions.

JSON actions cannot hold a server object between steps, so this module keeps at
most one running WebSocket mock and one running gRPC mock. Route and method
definitions use the JSON forms of :func:`route_from_config` and
:func:`configure_grpc_method`.
"""
from __future__ import annotations

import threading
from typing import Dict, List, Mapping, Optional, Union

from je_api_testka.utils.exception.exceptions import MockServerException
from je_api_testka.utils.mock_server.grpc_stub import (
    DEFAULT_GRPC_MOCK_HOST,
    DEFAULT_GRPC_MOCK_PORT,
    GrpcStubServer,
    configure_grpc_method,
)
from je_api_testka.utils.mock_server.websocket_mock import (
    DEFAULT_WS_MOCK_HOST,
    DEFAULT_WS_MOCK_PORT,
    WebSocketMockServer,
    route_from_config,
)

_WEBSOCKET: str = "websocket"
_GRPC: str = "grpc"
_MockServer = Union[WebSocketMockServer, GrpcStubServer]
_running: Dict[str, _MockServer] = {}
_lock = threading.Lock()


def _claim(kind: str, server: _MockServer) -> None:
    with _lock:
        if kind in _running:
            raise MockServerException(f"a {kind} mock is already running; stop it first")
        _running[kind] = server


def _running_server(kind: str) -> _MockServer:
    with _lock:
        server = _running.get(kind)
    if server is None:
        raise MockServerException(f"no {kind} mock is running")
    return server


def start_websocket_mock(routes: Optional[Mapping[str, Mapping[str, object]]] = None,
                         host: str = DEFAULT_WS_MOCK_HOST, port: int = DEFAULT_WS_MOCK_PORT) -> str:
    """
    Start the WebSocket mock and return its base URL.

    ``routes`` maps a path to its JSON route form; without routes, ``/`` echoes.
    """
    server = WebSocketMockServer(host, port)
    for path, config in (routes or {"/": {}}).items():
        server.add_route(path, route_from_config(config))
    _claim(_WEBSOCKET, server)
    try:
        return server.start()
    except Exception:
        with _lock:
            _running.pop(_WEBSOCKET, None)
        raise


def stop_websocket_mock() -> None:
    """Stop the WebSocket mock if one is running."""
    with _lock:
        server = _running.pop(_WEBSOCKET, None)
    if server is not None:
        server.stop()


def websocket_mock_received(path: str) -> List[str]:
    """Return the text frames the running WebSocket mock received on ``path``."""
    return _running_server(_WEBSOCKET).received(path)


def start_grpc_mock(methods: Mapping[str, Mapping[str, object]], host: str = DEFAULT_GRPC_MOCK_HOST,
                    port: int = DEFAULT_GRPC_MOCK_PORT) -> str:
    """
    Start the gRPC mock and return its ``host:port`` address.

    ``methods`` maps a full method path (``/package.Service/Method``) to its JSON form.
    """
    if not methods:
        raise MockServerException("a gRPC mock needs at least one method")
    server = GrpcStubServer(host, port)
    for method_path, config in methods.items():
        configure_grpc_method(server, method_path, config)
    _claim(_GRPC, server)
    try:
        return server.start()
    except Exception:
        with _lock:
            _running.pop(_GRPC, None)
        raise


def stop_grpc_mock() -> None:
    """Stop the gRPC mock if one is running."""
    with _lock:
        server = _running.pop(_GRPC, None)
    if server is not None:
        server.stop()


def grpc_mock_received(method_path: str) -> List[str]:
    """Return the requests the running gRPC mock received on ``method_path``, decoded as UTF-8."""
    return [request.decode("utf-8", errors="replace")
            for request in _running_server(_GRPC).received(method_path)]
