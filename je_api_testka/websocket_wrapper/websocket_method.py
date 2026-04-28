"""
WebSocket wrapper - sync and async send/receive helpers.

Optional dependency: ``websockets`` (install via ``pip install websockets``).
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Iterable, List, Optional

from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_WS_TIMEOUT_SECONDS: float = 10.0
WEBSOCKETS_NOT_INSTALLED: str = (
    "websockets package is not installed. Install with `pip install websockets`."
)


def _import_websockets():
    try:
        import websockets  # type: ignore
        return websockets
    except ImportError as error:
        apitestka_logger.error(f"websocket_method import websockets failed: {repr(error)}")
        raise APITesterException(WEBSOCKETS_NOT_INSTALLED) from error


async def _async_send_recv(
    url: str,
    messages: Iterable[str],
    expected_replies: int,
    timeout: float,
) -> List[str]:
    websockets = _import_websockets()
    received: List[str] = []
    async with websockets.connect(url, open_timeout=timeout) as connection:
        for message in messages:
            await connection.send(message)
        for _ in range(expected_replies):
            received.append(await asyncio.wait_for(connection.recv(), timeout=timeout))
    return received


def test_api_method_websocket_async(
    url: str,
    messages: Optional[Iterable[str]] = None,
    expected_replies: int = 1,
    timeout: float = DEFAULT_WS_TIMEOUT_SECONDS,
    record_request_info: bool = True,
) -> dict:
    """
    Async-friendly wrapper. Returns a dict with ``messages_sent`` and ``messages_received``.

    :param url: WebSocket URL (ws:// or wss://).
    :param messages: Iterable of text frames to send.
    :param expected_replies: How many frames to await before closing.
    :param timeout: Socket timeout in seconds.
    :param record_request_info: When True, push the result into ``test_record_instance``.
    """
    apitestka_logger.info(
        f"websocket_method test_api_method_websocket_async url: {url} "
        f"expected_replies: {expected_replies} timeout: {timeout}"
    )
    payloads = list(messages or [])
    start_time = datetime.now()
    try:
        received = asyncio.run(_async_send_recv(url, payloads, expected_replies, timeout))
    except Exception as error:
        apitestka_logger.error(f"websocket_method async failed: {repr(error)}")
        test_record_instance.error_record_list.append([
            {"url": url, "messages": payloads, "expected_replies": expected_replies},
            repr(error),
        ])
        raise
    end_time = datetime.now()
    record = {
        "url": url,
        "messages_sent": payloads,
        "messages_received": received,
        "start_time": str(start_time),
        "end_time": str(end_time),
    }
    if record_request_info:
        test_record_instance.test_record_list.append(record)
    return record


def test_api_method_websocket(
    url: str,
    messages: Optional[Iterable[str]] = None,
    expected_replies: int = 1,
    timeout: float = DEFAULT_WS_TIMEOUT_SECONDS,
    record_request_info: bool = True,
) -> dict:
    """Synchronous WebSocket round trip. Same parameters as the async version."""
    return test_api_method_websocket_async(
        url=url,
        messages=messages,
        expected_replies=expected_replies,
        timeout=timeout,
        record_request_info=record_request_info,
    )
