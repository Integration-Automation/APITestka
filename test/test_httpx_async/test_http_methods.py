from je_api_testka import test_api_method_httpx_async as api_httpx_async


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


async def test_get():
    response = await api_httpx_async("get", "http://httpbin.org/get")
    _assert_valid_response(response, "GET")
    data = response["response_data"]
    assert data.get("content") is not None
    assert data.get("cookies") is not None
    assert data.get("request_url") is not None
    assert data.get("request_time_sec") >= 0


async def test_post():
    response = await api_httpx_async("post", "http://httpbin.org/post",
                                                  params={"task": "new task"})
    _assert_valid_response(response, "POST")


async def test_put():
    response = await api_httpx_async("put", "http://httpbin.org/put",
                                                  params={"task": "new task"})
    _assert_valid_response(response, "PUT")


async def test_patch():
    response = await api_httpx_async("patch", "http://httpbin.org/patch",
                                                  params={"task": "new task"})
    _assert_valid_response(response, "PATCH")


async def test_delete():
    response = await api_httpx_async("delete", "http://httpbin.org/delete")
    _assert_valid_response(response, "DELETE")


async def test_head():
    response = await api_httpx_async("head", "http://httpbin.org/get", headers={
        "x-requested-with": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    _assert_valid_response(response, "HEAD")


async def test_options():
    response = await api_httpx_async("options", "http://httpbin.org/get", timeout=30)
    _assert_valid_response(response, "OPTIONS")


async def test_invalid_url():
    """Invalid URL should be caught and recorded as error (not raise)."""
    result = await api_httpx_async("get", "not_a_valid_url")
    assert result is None


async def test_invalid_method():
    """Invalid HTTP method should be caught and recorded as error."""
    result = await api_httpx_async("invalid_method", "http://httpbin.org/get")
    assert result is None
