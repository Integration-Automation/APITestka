"""
WebSocket mock endpoints.

:class:`WebSocketMockServer` serves scripted WebSocket routes from a background
thread (the ``websocket`` extra's ``websockets`` package, imported lazily).
Each route may greet a new connection, answer known messages from a reply map,
and handle the rest with a fallback; ``{{message}}`` in a reply is replaced by
the incoming message, so the default fallback echoes. Every text frame a route
receives is kept for later assertions. An unknown path is refused with HTTP 404
before the handshake.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Union
from urllib.parse import urlsplit

from je_api_testka.utils.exception.exceptions import MockServerException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

MESSAGE_PLACEHOLDER: str = "{{message}}"
WEBSOCKETS_MISSING: str = "websockets is not installed. Install with `pip install je_api_testka[websocket]`."
DEFAULT_WS_MOCK_HOST: str = "127.0.0.1"
DEFAULT_WS_MOCK_PORT: int = 8765
_JOIN_TIMEOUT_SECONDS: float = 5.0

Reply = Union[str, Sequence[str], None]
MessageHandler = Callable[[str], Reply]


def _import_sync_server():
    try:
        from websockets.sync import server  # type: ignore
    except ImportError as error:
        raise MockServerException(WEBSOCKETS_MISSING) from error
    return server


@dataclass
class WebSocketRoute:
    """
    Scripted behaviour of one WebSocket path.

    :param replies: exact incoming message → reply (a string or a list of frames).
    :param fallback: reply for any other message; ``None`` sends nothing.
    :param greeting: frame sent as soon as a client connects.
    :param handler: optional callable overriding ``replies`` and ``fallback``.
    """

    replies: Dict[str, Reply] = field(default_factory=dict)
    fallback: Optional[str] = MESSAGE_PLACEHOLDER
    greeting: Optional[str] = None
    handler: Optional[MessageHandler] = None

    def answer(self, message: str) -> List[str]:
        """Return the frames to send back for ``message`` (possibly none)."""
        reply = self.handler(message) if self.handler is not None else self.replies.get(message, self.fallback)
        if reply is None:
            return []
        frames = [reply] if isinstance(reply, str) else list(reply)
        return [str(frame).replace(MESSAGE_PLACEHOLDER, message) for frame in frames]


class WebSocketMockServer:
    """Scripted WebSocket server for tests. Port 0 picks a free port, readable from :attr:`port`."""

    def __init__(self, host: str = DEFAULT_WS_MOCK_HOST, port: int = DEFAULT_WS_MOCK_PORT) -> None:
        self.host = host
        self.port = port
        self._routes: Dict[str, WebSocketRoute] = {}
        self._received: Dict[str, List[str]] = {}
        self._lock = threading.Lock()
        self._server = None
        self._thread: Optional[threading.Thread] = None

    def add_route(self, path: str, route: Optional[WebSocketRoute] = None) -> WebSocketRoute:
        """Serve ``path`` with ``route`` (an echo route by default) and return it."""
        if not path.startswith("/"):
            raise MockServerException(f"websocket route must start with '/': {path!r}")
        self._routes[path] = route or WebSocketRoute()
        return self._routes[path]

    def received(self, path: str) -> List[str]:
        """Return a copy of the text frames received on ``path`` so far."""
        with self._lock:
            return list(self._received.get(path, []))

    @property
    def url(self) -> str:
        """Base ``ws://host:port`` URL; append a route path to connect."""
        return f"ws://{self.host}:{self.port}"

    def start(self) -> str:
        """Start serving in a daemon thread and return :attr:`url`."""
        if self._server is not None:
            raise MockServerException("websocket mock server is already running")
        server_module = _import_sync_server()
        self._server = server_module.serve(self._handle, self.host, self.port,
                                           process_request=self._reject_unknown_path)
        self.port = self._server.socket.getsockname()[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        apitestka_logger.info(f"WebSocketMockServer listening on {self.url}")
        return self.url

    def stop(self) -> None:
        """Stop serving and close open connections; a no-op when not running."""
        if self._server is None:
            return
        self._server.shutdown()
        if self._thread is not None:
            self._thread.join(_JOIN_TIMEOUT_SECONDS)
        self._server = None
        self._thread = None

    def __enter__(self) -> "WebSocketMockServer":
        self.start()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.stop()

    def _reject_unknown_path(self, connection, request):
        if urlsplit(request.path).path in self._routes:
            return None
        # protocol.reject also exists on websockets 12, where ServerConnection.respond does not.
        return connection.protocol.reject(HTTPStatus.NOT_FOUND, f"no websocket route for {request.path}\n")

    def _handle(self, connection) -> None:
        path = urlsplit(connection.request.path).path
        route = self._routes[path]
        if route.greeting is not None:
            connection.send(route.greeting)
        for message in connection:
            text = message if isinstance(message, str) else message.decode("utf-8", errors="replace")
            with self._lock:
                self._received.setdefault(path, []).append(text)
            for frame in route.answer(text):
                connection.send(frame)


def route_from_config(config: Mapping[str, object]) -> WebSocketRoute:
    """
    Build a :class:`WebSocketRoute` from its JSON form.

    Keys: ``replies`` (object), ``fallback`` (string or null), ``greeting`` (string).
    A missing ``fallback`` echoes.

    :raises MockServerException: on an unknown key or a value of the wrong type.
    """
    unknown = set(config) - {"replies", "fallback", "greeting"}
    if unknown:
        raise MockServerException(f"unknown websocket route keys: {sorted(unknown)}")
    replies = config.get("replies", {})
    fallback = config.get("fallback", MESSAGE_PLACEHOLDER)
    greeting = config.get("greeting")
    if not isinstance(replies, dict):
        raise MockServerException("websocket 'replies' must be an object")
    if fallback is not None and not isinstance(fallback, str):
        raise MockServerException("websocket 'fallback' must be a string or null")
    if greeting is not None and not isinstance(greeting, str):
        raise MockServerException("websocket 'greeting' must be a string")
    return WebSocketRoute(replies=dict(replies), fallback=fallback, greeting=greeting)
