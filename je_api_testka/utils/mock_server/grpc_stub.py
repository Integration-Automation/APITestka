"""
gRPC mock endpoints.

``grpcio`` is optional (the ``grpc`` extra) and imported lazily.
:class:`GrpcStubServer` serves methods by their full path
(``/package.Service/Method``) without compiled stubs:

* unary methods answer with a fixed payload (:meth:`GrpcStubServer.add_unary_response`)
  or a ``bytes -> bytes`` callable (:meth:`GrpcStubServer.register`);
* server-streaming methods answer with several messages
  (:meth:`GrpcStubServer.add_stream_responses`, :meth:`GrpcStubServer.register_server_stream`);
* :meth:`GrpcStubServer.add_error` makes a method fail with a gRPC status code.

Payloads are raw bytes on the wire: ``bytes`` pass through, ``str`` is UTF-8 and
any other JSON value (object, array, number, boolean, null) is compact JSON. Serialized protobuf messages
(``message.SerializeToString()``) therefore work with generated clients, and JSON
payloads suit clients that use JSON (de)serializers. Every request is kept per
method for later assertions.
"""
from __future__ import annotations

import base64
import binascii
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Iterable, List, Mapping, Sequence, Tuple, Union

from je_api_testka.utils.exception.exceptions import MockServerException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

GRPCIO_NOT_INSTALLED: str = "grpcio is not installed. Install with `pip install je_api_testka[grpc]`."
DEFAULT_GRPC_MOCK_HOST: str = "127.0.0.1"
DEFAULT_GRPC_MOCK_PORT: int = 50051
_MAX_WORKERS: int = 4
_STOP_WAIT_SECONDS: float = 5.0
_UNARY: str = "unary"
_STREAM: str = "stream"

Payload = Union[bytes, str, dict, list, int, float, bool, None]


def is_grpc_available() -> bool:
    """Return True when ``grpcio`` can be imported."""
    try:
        import grpc  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


def encode_payload(value: Payload) -> bytes:
    """Return the wire bytes for ``value``: bytes as-is, str as UTF-8, any other JSON value as compact JSON."""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, str):
        return value.encode("utf-8")
    if value is None or isinstance(value, (dict, list, int, float, bool)):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    raise MockServerException(f"unsupported gRPC payload type: {type(value).__name__}")


class GrpcStubServer:
    """Generic-handler gRPC server for tests. Port 0 picks a free port, readable from :attr:`port`."""

    def __init__(self, host: str = DEFAULT_GRPC_MOCK_HOST, port: int = DEFAULT_GRPC_MOCK_PORT) -> None:
        if not is_grpc_available():
            raise MockServerException(GRPCIO_NOT_INSTALLED)
        import grpc  # type: ignore
        self._grpc = grpc
        self._server = grpc.server(ThreadPoolExecutor(max_workers=_MAX_WORKERS))
        self._methods: Dict[str, Tuple[str, Callable]] = {}
        self._received: Dict[str, List[bytes]] = {}
        self._lock = threading.Lock()
        self._started = False
        self.host = host
        self.port = self._server.add_insecure_port(f"{host}:{port}")

    @property
    def address(self) -> str:
        """``host:port`` to pass to ``grpc.insecure_channel``."""
        return f"{self.host}:{self.port}"

    def register(self, method_path: str, handler: Callable[[bytes], bytes]) -> None:
        """Register a unary handler: request bytes in, response bytes out."""
        self._methods[method_path] = (_UNARY, lambda request, _context: handler(request))

    def register_server_stream(self, method_path: str, handler: Callable[[bytes], Iterable[bytes]]) -> None:
        """Register a server-streaming handler: request bytes in, an iterable of response bytes out."""
        self._methods[method_path] = (_STREAM, lambda request, _context: iter(handler(request)))

    def add_unary_response(self, method_path: str, response: Payload) -> None:
        """Answer every call of a unary method with ``response``."""
        wire = encode_payload(response)
        self.register(method_path, lambda _request: wire)

    def add_stream_responses(self, method_path: str, responses: Sequence[Payload]) -> None:
        """Answer every call of a server-streaming method with ``responses``, in order."""
        wires = [encode_payload(response) for response in responses]
        self.register_server_stream(method_path, lambda _request: wires)

    def add_error(self, method_path: str, code: str, details: str = "") -> None:
        """Fail every unary call of ``method_path`` with gRPC status ``code`` (e.g. ``"NOT_FOUND"``)."""
        try:
            status = self._grpc.StatusCode[code.upper()]
        except KeyError as error:
            raise MockServerException(f"unknown gRPC status code: {code!r}") from error

        def _abort(_request: bytes, context) -> bytes:
            context.abort(status, details)
            return b""  # not reached: abort raises

        self._methods[method_path] = (_UNARY, _abort)

    def received(self, method_path: str) -> List[bytes]:
        """Return a copy of the request payloads received by ``method_path`` so far."""
        with self._lock:
            return list(self._received.get(method_path, []))

    def start(self) -> str:
        """Start serving and return :attr:`address`."""
        if self._started:
            raise MockServerException("gRPC mock server is already running")
        self._server.add_generic_rpc_handlers((_GenericService(self._lookup),))
        self._server.start()
        self._started = True
        apitestka_logger.info(f"GrpcStubServer listening on {self.address}")
        return self.address

    def stop(self, grace: float = 0.0) -> None:
        """Stop serving; in-flight calls get ``grace`` seconds to finish."""
        self._server.stop(grace).wait(_STOP_WAIT_SECONDS)
        self._started = False

    def __enter__(self) -> "GrpcStubServer":
        self.start()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.stop()

    def _lookup(self, handler_call_details):
        method_path = handler_call_details.method
        entry = self._methods.get(method_path)
        if entry is None:
            return None
        kind, behavior = entry

        def _recorded(request: bytes, context):
            with self._lock:
                self._received.setdefault(method_path, []).append(request)
            return behavior(request, context)

        if kind == _STREAM:
            return self._grpc.unary_stream_rpc_method_handler(_recorded)
        return self._grpc.unary_unary_rpc_method_handler(_recorded)


class _GenericService:
    """Adapter that lets us use a function as a generic RPC handler."""

    def __init__(self, callback) -> None:
        self._callback = callback

    def service(self, handler_call_details):
        return self._callback(handler_call_details)


def _config_payload(config: Mapping[str, object]) -> Payload:
    if "response_base64" in config:
        try:
            return base64.b64decode(str(config["response_base64"]), validate=True)
        except (binascii.Error, ValueError) as error:
            raise MockServerException("gRPC 'response_base64' is not valid base64") from error
    return config["response"]  # type: ignore[return-value]


def configure_grpc_method(server: GrpcStubServer, method_path: str, config: Mapping[str, object]) -> None:
    """
    Register one method from its JSON form.

    Exactly one of ``response`` (JSON value or string), ``response_base64`` (raw bytes,
    e.g. a serialized protobuf), ``stream`` (list of payloads) or
    ``error`` (``{"code": "NOT_FOUND", "details": "..."}``) must be given.

    :raises MockServerException: when none or several are given, or a value has the wrong type.
    """
    kinds = [key for key in ("response", "response_base64", "stream", "error") if key in config]
    if len(kinds) != 1 or set(config) - set(kinds):
        raise MockServerException(
            f"gRPC method {method_path} needs exactly one of response, response_base64, stream, error"
        )
    if "stream" in config:
        if not isinstance(config["stream"], list):
            raise MockServerException("gRPC 'stream' must be a list")
        server.add_stream_responses(method_path, config["stream"])
    elif "error" in config:
        error = config["error"]
        if not isinstance(error, dict) or not isinstance(error.get("code"), str):
            raise MockServerException("gRPC 'error' must be an object with a string 'code'")
        server.add_error(method_path, error["code"], str(error.get("details", "")))
    else:
        server.add_unary_response(method_path, _config_payload(config))
