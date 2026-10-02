"""Translate request results into the shared, opt-in request-record contract."""

from __future__ import annotations

import base64
from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from je_action_core.request_context import RunContext
    from je_action_core.request_record import RequestRecord

_SENSITIVE_HEADERS = frozenset(("authorization", "proxy-authorization", "cookie", "set-cookie", "x-api-key"))


def get_optional_run_context() -> RunContext | None:
    """Return the selected run, retaining legacy behavior with earlier ActionCore versions."""
    try:
        from je_action_core.request_context import get_run_context
    except ModuleNotFoundError as error:
        if error.name != "je_action_core.request_context":
            raise
        return None
    return get_run_context()


def _timestamp(value: object) -> object:
    return value.timestamp() if isinstance(value, datetime) else value


def _duration(record: Mapping[str, object]) -> object:
    elapsed = record.get("elapsed")
    if isinstance(elapsed, timedelta):
        return elapsed.total_seconds() * 1000
    seconds = record.get("request_time_sec")
    return float(seconds) * 1000 if seconds is not None else record.get("response_time_ms")


def _fields(record: Mapping[str, object]) -> dict[str, object]:
    method = str(record.get("request_method") or record.get("http_method") or "GET")
    method = method.removeprefix("session_").upper()
    url = str(record.get("request_url") or record.get("test_url") or "")
    content = record.get("content")
    return {"protocol": "http", "request_method": method, "request_url": url,
            "name": str(record.get("name") or f"{method} {url}"),
            "status_code": record.get("status_code"), "start_time": _timestamp(record.get("start_time")),
            "end_time": _timestamp(record.get("end_time")), "response_time_ms": _duration(record),
            "response_length": len(content) if isinstance(content, bytes) else record.get("response_length"),
            "assertions": record.get("assertions") or [], "error": record.get("error"),
            "outcome": record.get("outcome") or "passed", "step_id": record.get("step_id"),
            "scenario_id": record.get("scenario_id")}


def _payload(record: Mapping[str, object]) -> dict[str, object]:
    fields: dict[str, object] = {}
    if "text" in record:
        fields["text"] = record["text"]
    headers = record.get("headers")
    if isinstance(headers, Mapping):
        fields["headers"] = {str(key): "[REDACTED]" if str(key).lower() in _SENSITIVE_HEADERS else str(value)
                             for key, value in headers.items()}
    content = record.get("content")
    if isinstance(content, bytes):
        fields["content_base64"] = base64.b64encode(content).decode("ascii")
    if "request_body" in record:
        fields["request_body"] = record["request_body"]
    return fields


def from_legacy_record(record: Mapping[str, object] | list[object], context: RunContext,
                       capture_payload: bool = False) -> RequestRecord:
    """Import a success dictionary or legacy failure pair into a run; payload capture is opt-in."""
    if isinstance(record, list):
        if len(record) != 2 or not isinstance(record[0], Mapping) or not isinstance(record[1], str):
            raise ValueError("record: expected a request dictionary and error message")
        record = {**record[0], "outcome": "failed", "error": {"kind": "request", "message": record[1]}}
    if not isinstance(record, Mapping):
        raise ValueError("record: expected a result dictionary or failure pair")
    fields = _fields(record)
    if capture_payload:
        fields.update(_payload(record))
    return context.capture(fields)
