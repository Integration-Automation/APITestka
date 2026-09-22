"""TLS certificate checks are on unless a caller turns them off."""
import inspect

import pytest

from je_api_testka.httpx_wrapper import httpx_method
from je_api_testka.requests_wrapper import request_method


@pytest.mark.parametrize("function", [
    request_method.send_requests,
    request_method.test_api_method_requests,
    httpx_method.send_httpx_requests,
    httpx_method.test_api_method_httpx,
], ids=lambda function: function.__name__)
def test_verify_defaults_to_true(function):
    assert inspect.signature(function).parameters["verify"].default is True


def test_verify_reaches_requests(monkeypatch):
    seen = {}

    def fake_get(url, **kwargs):
        seen.update(kwargs)
        raise ConnectionError("stop here")

    monkeypatch.setitem(request_method.http_method_dict, "get", fake_get)
    request_method.test_api_method_requests("get", "https://example.test/")
    assert seen["verify"] is True


def test_soap_request_keeps_the_callers_options(monkeypatch):
    seen = {}

    def fake_post(url, **kwargs):
        seen.update(kwargs)
        raise ConnectionError("stop here")

    monkeypatch.setitem(request_method.http_method_dict, "post", fake_post)
    request_method.test_api_method_requests("post", "https://example.test/soap", soap=True,
                                            verify=False, timeout=9, allow_redirects=True)
    assert (seen["verify"], seen["timeout"], seen["allow_redirects"]) == (False, 9, True)
    assert seen["headers"]["Content-Type"] == "application/soap+xml"
