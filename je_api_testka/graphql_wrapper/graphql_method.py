"""
GraphQL helper - builds the request body and forwards to the httpx wrappers.
"""
from __future__ import annotations

from typing import Optional

from je_api_testka.httpx_wrapper.async_httpx_method import test_api_method_httpx_async
from je_api_testka.httpx_wrapper.httpx_method import test_api_method_httpx
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_GRAPHQL_TIMEOUT_SECONDS: int = 30


def _build_payload(query: str, variables: Optional[dict], operation_name: Optional[str]) -> dict:
    payload: dict = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    if operation_name is not None:
        payload["operationName"] = operation_name
    return payload


def test_api_method_graphql(
    url: str,
    query: str,
    variables: Optional[dict] = None,
    operation_name: Optional[str] = None,
    headers: Optional[dict] = None,
    timeout: int = DEFAULT_GRAPHQL_TIMEOUT_SECONDS,
    **kwargs,
) -> Optional[dict]:
    """Send a GraphQL POST request and return the recorded response payload."""
    apitestka_logger.info(
        f"graphql_method test_api_method_graphql url: {url} operation_name: {operation_name}"
    )
    payload = _build_payload(query, variables, operation_name)
    return test_api_method_httpx(
        http_method="post",
        test_url=url,
        json=payload,
        headers=headers or {"Content-Type": "application/json"},
        timeout=timeout,
        **kwargs,
    )


async def test_api_method_graphql_async(
    url: str,
    query: str,
    variables: Optional[dict] = None,
    operation_name: Optional[str] = None,
    headers: Optional[dict] = None,
    timeout: int = DEFAULT_GRAPHQL_TIMEOUT_SECONDS,  # NOSONAR S7483: httpx request timeout, not asyncio.wait_for
    **kwargs,
) -> Optional[dict]:
    """Async variant of :func:`test_api_method_graphql`."""
    apitestka_logger.info(
        f"graphql_method test_api_method_graphql_async url: {url} operation_name: {operation_name}"
    )
    payload = _build_payload(query, variables, operation_name)
    return await test_api_method_httpx_async(
        http_method="post",
        test_url=url,
        json=payload,
        headers=headers or {"Content-Type": "application/json"},
        timeout=timeout,
        **kwargs,
    )
