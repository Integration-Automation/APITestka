from je_api_testka import test_api_method_httpx_async as api_httpx_async


async def test_get(mock_url, assert_valid_response, assert_get_extras):
    response = await api_httpx_async("get", f"{mock_url}/get", timeout=30)
    assert_valid_response(response, "GET")
    assert_get_extras(response)


async def test_post(mock_url, assert_valid_response):
    response = await api_httpx_async(
        "post", f"{mock_url}/post", params={"task": "new task"}, timeout=30,
    )
    assert_valid_response(response, "POST")


async def test_put(mock_url, assert_valid_response):
    response = await api_httpx_async(
        "put", f"{mock_url}/put", params={"task": "new task"}, timeout=30,
    )
    assert_valid_response(response, "PUT")


async def test_patch(mock_url, assert_valid_response):
    response = await api_httpx_async(
        "patch", f"{mock_url}/patch", params={"task": "new task"}, timeout=30,
    )
    assert_valid_response(response, "PATCH")


async def test_delete(mock_url, assert_valid_response):
    response = await api_httpx_async("delete", f"{mock_url}/delete", timeout=30)
    assert_valid_response(response, "DELETE")


async def test_head(mock_url, assert_valid_response):
    response = await api_httpx_async("head", f"{mock_url}/get", headers={
        "x-requested-with": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    }, timeout=30)
    assert_valid_response(response, "HEAD")


async def test_options(mock_url, assert_valid_response):
    response = await api_httpx_async("options", f"{mock_url}/get", timeout=30)
    assert_valid_response(response, "OPTIONS")


async def test_invalid_url():
    assert await api_httpx_async("get", "not_a_valid_url", timeout=30) is None


async def test_invalid_method(mock_url):
    assert await api_httpx_async("invalid_method", f"{mock_url}/get", timeout=30) is None
