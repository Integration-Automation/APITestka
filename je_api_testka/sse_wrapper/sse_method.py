"""
Server-Sent Events (SSE) helper using httpx streaming.

Provides a generator over SSE events and a one-shot test helper that records
the captured events into ``test_record_instance``.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Generator, List, Optional

import httpx

from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_SSE_TIMEOUT_SECONDS: float = 30.0
SSE_DATA_PREFIX: str = "data:"
SSE_EVENT_PREFIX: str = "event:"
SSE_ID_PREFIX: str = "id:"


def _flush_event(buffer: Dict[str, str]) -> Optional[Dict[str, str]]:
    if not buffer.get("data"):
        return None
    event = dict(buffer)
    buffer.clear()
    return event


def iter_sse_events(
    url: str,
    max_events: int = 50,
    timeout: float = DEFAULT_SSE_TIMEOUT_SECONDS,
    headers: Optional[dict] = None,
) -> Generator[Dict[str, str], None, None]:
    """
    Yield SSE events from ``url`` until ``max_events`` are received or the stream closes.
    """
    apitestka_logger.info(
        f"sse_method iter_sse_events url: {url} max_events: {max_events} timeout: {timeout}"
    )
    request_headers = {"Accept": "text/event-stream"}
    if headers:
        request_headers.update(headers)
    buffer: Dict[str, str] = {}
    yielded = 0
    with httpx.stream("GET", url, headers=request_headers, timeout=timeout) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                event = _flush_event(buffer)
                if event is not None:
                    yield event
                    yielded += 1
                    if yielded >= max_events:
                        return
                continue
            if line.startswith(SSE_DATA_PREFIX):
                buffer.setdefault("data", "")
                buffer["data"] += line[len(SSE_DATA_PREFIX):].lstrip()
            elif line.startswith(SSE_EVENT_PREFIX):
                buffer["event"] = line[len(SSE_EVENT_PREFIX):].strip()
            elif line.startswith(SSE_ID_PREFIX):
                buffer["id"] = line[len(SSE_ID_PREFIX):].strip()


def test_api_method_sse(
    url: str,
    max_events: int = 5,
    timeout: float = DEFAULT_SSE_TIMEOUT_SECONDS,
    headers: Optional[dict] = None,
    record_request_info: bool = True,
) -> dict:
    """Collect ``max_events`` SSE messages and return them as a record dictionary."""
    apitestka_logger.info(f"sse_method test_api_method_sse url: {url}")
    start_time = datetime.now()
    events: List[Dict[str, str]] = []
    try:
        for event in iter_sse_events(url, max_events=max_events, timeout=timeout, headers=headers):
            events.append(event)
    except httpx.HTTPError as error:
        apitestka_logger.error(f"sse_method failed: {repr(error)}")
        test_record_instance.error_record_list.append([
            {"url": url, "max_events": max_events},
            repr(error),
        ])
        raise
    end_time = datetime.now()
    record = {
        "url": url,
        "events": events,
        "start_time": str(start_time),
        "end_time": str(end_time),
    }
    if record_request_info:
        test_record_instance.test_record_list.append(record)
    return record
