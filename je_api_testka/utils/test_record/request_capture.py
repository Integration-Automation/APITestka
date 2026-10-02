"""Capture wrapper outcomes without changing their native return values or legacy records."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Mapping
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps
from time import monotonic, time
from typing import TYPE_CHECKING, cast

from httpx import InvalidURL, RequestError, UnsupportedProtocol
from requests.exceptions import RequestException

from je_api_testka.utils.exception.exceptions import APIAssertException, APICheckException, APITesterException
from je_api_testka.utils.test_record.contract import from_legacy_record, get_optional_run_context

if TYPE_CHECKING:
    from je_action_core.request_context import RunContext


@dataclass
class _PendingRequest:
    arguments: Mapping[str, object]
    context: RunContext
    start_time: float = field(default_factory=lambda: time())
    clock: float = field(default_factory=lambda: monotonic())
    response: dict[str, object] | None = None
    error: Exception | None = None
    response_received: bool = False


_pending_request: ContextVar[_PendingRequest | None] = ContextVar("apitestka_pending_request", default=None)


def note_response(response: dict[str, object]) -> None:
    """Keep response metadata before status validation can raise an exception."""
    pending = _pending_request.get()
    if pending is not None:
        pending.response = response


def note_response_received(status_code: int, content: bytes) -> None:
    """Retain transport evidence even if subsequent legacy metadata conversion fails."""
    pending = _pending_request.get()
    if pending is not None:
        pending.response_received = True
        pending.response = {"status_code": status_code, "content": content}


def note_error(error: Exception) -> None:
    """Keep the original failure before the legacy wrapper converts it to a failure pair."""
    pending = _pending_request.get()
    if pending is not None:
        pending.error = error


def _is_tls_failure(error: BaseException) -> bool:
    visited: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        name = type(current).__name__.lower()
        if "ssl" in name or "tls" in name:
            return True
        current = current.__cause__ or current.__context__
    return False


def _error_kind(error: Exception) -> str:
    if isinstance(error, (APIAssertException, APICheckException)):
        return "assertion"
    name = type(error).__name__.lower()
    if "httpstatus" in name or "httperror" in name:
        return "http_status"
    if "timeout" in name:
        return "timeout"
    if _is_tls_failure(error):
        return "tls"
    if "connect" in name:
        return "connection"
    if isinstance(error, (RequestError, RequestException, OSError)):
        return "transport"
    return "runner_internal"


def _assertions(pending: _PendingRequest) -> list[dict[str, object]]:
    checks = pending.arguments.get("result_check_dict")
    if not isinstance(checks, Mapping) or pending.response is None:
        return []
    if pending.error is not None and _error_kind(pending.error) != "assertion":
        return []
    assertions = []
    for key, expected in checks.items():
        passed = pending.response.get(key) == expected
        assertion = {"type": str(key), "passed": passed}
        if not passed:
            assertion["message"] = f"value should be {expected} but value was {pending.response.get(key)}"
        assertions.append(assertion)
        if not passed:
            break
    return assertions


def _finish(pending: _PendingRequest) -> None:
    if pending.response is None and pending.error is None:
        return  # A SOAP wrapper delegates to another captured invocation.
    if pending.error is None and not pending.arguments.get("record_request_info", True):
        return
    configuration_errors = (APITesterException, ValueError, TypeError, InvalidURL, UnsupportedProtocol)
    if not pending.response_received and isinstance(pending.error, configuration_errors):
        return
    record = {**pending.arguments, **(pending.response or {})}
    elapsed = monotonic() - pending.clock
    record.update(start_time=pending.start_time, end_time=pending.start_time + elapsed,
                  elapsed=None, request_time_sec=elapsed,
                  assertions=_assertions(pending), outcome="failed" if pending.error else "passed")
    if pending.error is not None:
        record["error"] = {"kind": _error_kind(pending.error),
                           "message": str(pending.error) or repr(pending.error)}
    from_legacy_record(record, pending.context)


def _begin(signature: inspect.Signature, args: tuple[object, ...],
           kwargs: dict[str, object]) -> _PendingRequest | None:
    context = get_optional_run_context()
    if context is None:
        return None
    arguments = signature.bind(*args, **kwargs)
    arguments.apply_defaults()
    return _PendingRequest(arguments.arguments, context)


def _wrap_sync(function: Callable[..., object], signature: inspect.Signature) -> Callable[..., object]:
    @wraps(function)
    def sync_wrapper(*args: object, **kwargs: object) -> object:
        pending = _begin(signature, args, kwargs)
        token = _pending_request.set(pending)
        try:
            return function(*args, **kwargs)
        except Exception as error:
            note_error(error)
            raise
        finally:
            _pending_request.reset(token)
            if pending is not None:
                _finish(pending)

    return sync_wrapper


def _wrap_async(function: Callable[..., object], signature: inspect.Signature) -> Callable[..., object]:
    @wraps(function)
    async def async_wrapper(*args: object, **kwargs: object) -> object:
        pending = _begin(signature, args, kwargs)
        token = _pending_request.set(pending)
        try:
            return await cast(Awaitable[object], function(*args, **kwargs))
        except Exception as error:
            note_error(error)
            raise
        finally:
            _pending_request.reset(token)
            if pending is not None:
                _finish(pending)

    return async_wrapper


def capture_api_request(function: Callable[..., object]) -> Callable[..., object]:
    """Decorate a sync or async request wrapper with context-local outcome capture."""
    signature = inspect.signature(function)
    factory = _wrap_async if inspect.iscoroutinefunction(function) else _wrap_sync
    return factory(function, signature)
