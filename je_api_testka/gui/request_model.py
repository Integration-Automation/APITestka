"""
Qt-free model behind the GUI's request page.

:class:`RequestSpec` is what the page collects; :func:`send_request` renders
``{{variable}}`` placeholders from the variable store (filled by the active
environment), sends the request through the chosen backend and returns the
recorded response data; :func:`describe_response` turns that into what the
response viewer shows. Keeping this apart from the widgets makes it testable
without a display.
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from je_api_testka.data.template_render import render_template
from je_api_testka.data.variable_store import variable_store
from je_api_testka.httpx_wrapper.async_httpx_method import test_api_method_httpx_async
from je_api_testka.httpx_wrapper.httpx_method import test_api_method_httpx
from je_api_testka.requests_wrapper.request_method import test_api_method_requests
from je_api_testka.utils.exception.exceptions import APITesterException

BACKENDS = ("requests", "httpx", "httpx_async")
HTTP_METHODS = ("get", "post", "put", "patch", "delete", "head", "options")
SESSION_METHODS = tuple(f"session_{method}" for method in HTTP_METHODS)
DEFAULT_TIMEOUT_SECONDS: int = 10
_SERVER_ERROR: int = 500
_CLIENT_ERROR: int = 400
_REDIRECT: int = 300


def parse_json_field(text: str, field_name: str) -> Optional[Any]:
    """
    Parse a JSON input box; an empty box is ``None``.

    :raises ValueError: naming ``field_name`` when the text is not JSON.
    """
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"{field_name}: not valid JSON ({error.msg}, line {error.lineno})") from error


def parse_body(text: str) -> Optional[Any]:
    """Return the body box as JSON when it parses, as text otherwise, ``None`` when empty."""
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


@dataclass
class RequestSpec:
    """One request as the request page describes it."""

    method: str
    url: str
    backend: str = "httpx"
    params: Optional[dict] = None
    headers: Optional[dict] = None
    body: Optional[Any] = None
    auth: Optional[dict] = None
    timeout: int = DEFAULT_TIMEOUT_SECONDS
    verify: bool = True
    allow_redirects: bool = False
    soap: bool = False
    result_check: Optional[dict] = None


def _render(value: Any) -> Any:
    return None if value is None else render_template(value, store=variable_store)


def _request_kwargs(spec: RequestSpec) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    for key, value in (("params", spec.params), ("headers", spec.headers)):
        if value:
            kwargs[key] = _render(value)
    body = _render(spec.body)
    if isinstance(body, (dict, list)):
        kwargs["json"] = body
    elif body is not None:
        kwargs["data"] = body
    if isinstance(spec.auth, Mapping):
        kwargs["auth"] = (str(spec.auth.get("username", "")), str(spec.auth.get("password", "")))
    return kwargs


def _call_backend(spec: RequestSpec, url: str, kwargs: Dict[str, Any]) -> Any:
    common = {"http_method": spec.method, "test_url": url, "result_check_dict": spec.result_check,
              "timeout": spec.timeout, **kwargs}
    if spec.backend == "requests":
        return test_api_method_requests(soap=spec.soap, verify=spec.verify,
                                        allow_redirects=spec.allow_redirects, **common)
    if spec.backend == "httpx":
        return test_api_method_httpx(verify=spec.verify, **common)
    if spec.backend == "httpx_async":
        return asyncio.run(test_api_method_httpx_async(**common))
    raise APITesterException(f"unknown backend {spec.backend!r}; expected one of {BACKENDS}")


def send_request(spec: RequestSpec) -> dict:
    """
    Send ``spec`` and return the recorded response data.

    :raises APITesterException: when the URL is empty, the backend is unknown or the request failed
        (the failure is also in the error records).
    """
    url = str(_render(spec.url.strip()))
    if not url:
        raise APITesterException("the URL is empty")
    result = _call_backend(spec, url, _request_kwargs(spec))
    if not isinstance(result, dict) or not isinstance(result.get("response_data"), dict):
        raise APITesterException("the request failed; see the error records")
    return result["response_data"]


@dataclass
class ResponseView:
    """What the response viewer shows for one response."""

    status: int
    status_class: str
    elapsed_ms: float
    size_bytes: int
    body: str
    headers: str


def _status_class(status: int) -> str:
    if status >= _SERVER_ERROR:
        return "server-error"
    if status >= _CLIENT_ERROR:
        return "client-error"
    if status >= _REDIRECT:
        return "redirect"
    return "success"


def describe_response(response_data: Mapping[str, Any]) -> ResponseView:
    """Summarize recorded response data: status, time, size, pretty body and header lines."""
    text = str(response_data.get("text") or "")
    try:
        body = json.dumps(json.loads(text), indent=2, ensure_ascii=False) if text else ""
    except json.JSONDecodeError:
        body = text
    headers = response_data.get("headers") or {}
    header_lines = "\n".join(f"{name}: {value}" for name, value in dict(headers).items())
    content = response_data.get("content") or b""
    status = int(response_data.get("status_code") or 0)
    seconds = response_data.get("request_time_sec") or 0.0
    return ResponseView(status, _status_class(status), float(seconds) * 1000,
                        len(content) if isinstance(content, (bytes, str)) else 0, body, header_lines)
