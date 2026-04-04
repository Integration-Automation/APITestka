from je_api_testka import test_api_method_httpx as api_httpx


def _assert_valid_response(response, expected_method=None):
    """Helper to validate a successful response dict."""
    assert response is not None
    data = response.get("response_data")
    assert data is not None
    assert data.get("status_code") == 200
    assert data.get("text") is not None
    assert data.get("headers") is not None
    assert data.get("elapsed") is not None
    assert data.get("start_time") is not None
    assert data.get("end_time") is not None
    if expected_method:
        assert data.get("request_method") == expected_method


def test_get():
    response = api_httpx("get", "http://httpbin.org/get")
    _assert_valid_response(response, "GET")
    data = response["response_data"]
    assert data.get("content") is not None
    assert data.get("cookies") is not None
    assert data.get("request_url") is not None
    assert data.get("request_time_sec") >= 0


def test_post():
    response = api_httpx("post", "http://httpbin.org/post", params={"task": "new task"})
    _assert_valid_response(response, "POST")


def test_put():
    response = api_httpx("put", "http://httpbin.org/put", params={"task": "new task"})
    _assert_valid_response(response, "PUT")


def test_patch():
    response = api_httpx("patch", "http://httpbin.org/patch", params={"task": "new task"})
    _assert_valid_response(response, "PATCH")


def test_delete():
    response = api_httpx("delete", "http://httpbin.org/delete")
    _assert_valid_response(response, "DELETE")


def test_head():
    response = api_httpx("head", "http://httpbin.org/get", headers={
        "x-requested-with": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    _assert_valid_response(response, "HEAD")


def test_options():
    response = api_httpx("options", "http://httpbin.org/get")
    _assert_valid_response(response, "OPTIONS")


def test_invalid_url():
    """Invalid URL should be caught and recorded as error (not raise)."""
    result = api_httpx("get", "not_a_valid_url")
    assert result is None


def test_invalid_method():
    """Invalid HTTP method should be caught and recorded as error."""
    result = api_httpx("invalid_method", "http://httpbin.org/get")
    assert result is None
