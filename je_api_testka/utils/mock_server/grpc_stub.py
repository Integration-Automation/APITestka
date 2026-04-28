"""
gRPC mock stub.

We do not pull in the heavyweight ``grpcio`` package by default. This module
provides:

* :func:`is_grpc_available` checks whether the optional dependency exists.
* :class:`GrpcStubServer` lazily imports grpcio and exposes ``register`` /
  ``start`` / ``stop`` for unary RPCs only.

For full gRPC testing, install ``grpcio`` separately.
"""
from __future__ import annotations

from typing import Callable, Dict

from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

GRPCIO_NOT_INSTALLED: str = "grpcio not installed. Install with `pip install grpcio`."


def is_grpc_available() -> bool:
    try:
        import grpc  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


class GrpcStubServer:
    """Wrapper around a generic-handler-only gRPC server. Unary calls only."""

    def __init__(self, host: str = "127.0.0.1", port: int = 50051) -> None:
        if not is_grpc_available():
            raise APITesterException(GRPCIO_NOT_INSTALLED)
        import grpc  # type: ignore
        from concurrent.futures import ThreadPoolExecutor
        self._grpc = grpc
        self._server = grpc.server(ThreadPoolExecutor(max_workers=4))
        self._handlers: Dict[str, Callable[[bytes], bytes]] = {}
        self._address = f"{host}:{port}"
        self._server.add_insecure_port(self._address)
        apitestka_logger.info(f"GrpcStubServer listening on {self._address}")

    def register(self, method_path: str, handler: Callable[[bytes], bytes]) -> None:
        """Register a unary handler: bytes-in, bytes-out."""
        self._handlers[method_path] = handler

    def start(self) -> None:
        grpc = self._grpc

        def _generic(handler_call_details):
            handler = self._handlers.get(handler_call_details.method)
            if handler is None:
                return None
            return grpc.unary_unary_rpc_method_handler(
                lambda request, _ctx, fn=handler: fn(request),
                request_deserializer=lambda blob: blob,
                response_serializer=lambda blob: blob,
            )

        self._server.add_generic_rpc_handlers((_GenericService(_generic),))
        self._server.start()

    def stop(self, grace: float = 0.0) -> None:
        self._server.stop(grace)


class _GenericService:
    """Adapter that lets us use a function as a generic RPC handler."""

    def __init__(self, callback) -> None:
        self._callback = callback

    def service(self, handler_call_details):
        return self._callback(handler_call_details)
