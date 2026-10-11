"""
Build one requests-backend call in executor action form.

Every converter that turns outside input (OpenAPI, Postman, cURL, HAR, AI
output, scaffolds) into actions goes through :func:`build_request_action`, so
they all emit the ``[command, kwargs]`` shape and a command name that
``Executor.event_dict`` registers.
"""
from __future__ import annotations

from typing import Mapping, Optional

REQUEST_COMMAND: str = "AT_test_api_method"


def build_request_action(http_method: str, test_url: str, headers: Optional[Mapping[str, str]] = None,
                         body: object = None, **options: object) -> list:
    """
    Return ``["AT_test_api_method", {...}]`` for one request.

    A ``dict`` or ``list`` body is sent as ``json``; any other non-``None`` body
    as ``data``. ``options`` (``result_check_dict``, ``timeout``, runner ``tags``...)
    are copied into the kwargs unchanged.
    """
    kwargs: dict = {"http_method": http_method.lower(), "test_url": test_url}
    if headers:
        kwargs["headers"] = dict(headers)
    if isinstance(body, (dict, list)):
        kwargs["json"] = body
    elif body is not None:
        kwargs["data"] = body
    kwargs.update(options)
    return [REQUEST_COMMAND, kwargs]
