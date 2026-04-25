from je_api_testka import test_api_method_httpx as api_httpx


def test_get(mock_url, assert_valid_response, assert_get_extras):
    response = api_httpx("get", f"{mock_url}/get", timeout=30)
    assert_valid_response(response, "GET")
    assert_get_extras(response)


def test_post(mock_url, assert_valid_response):
    response = api_httpx("post", f"{mock_url}/post", params={"task": "new task"}, timeout=30)
    assert_valid_response(response, "POST")


def test_put(mock_url, assert_valid_response):
    response = api_httpx("put", f"{mock_url}/put", params={"task": "new task"}, timeout=30)
    assert_valid_response(response, "PUT")


def test_patch(mock_url, assert_valid_response):
    response = api_httpx("patch", f"{mock_url}/patch", params={"task": "new task"}, timeout=30)
    assert_valid_response(response, "PATCH")


def test_delete(mock_url, assert_valid_response):
    response = api_httpx("delete", f"{mock_url}/delete", timeout=30)
    assert_valid_response(response, "DELETE")


def test_head(mock_url, assert_valid_response):
    response = api_httpx("head", f"{mock_url}/get", headers={
        "x-requested-with": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    }, timeout=30)
    assert_valid_response(response, "HEAD")


def test_options(mock_url, assert_valid_response):
    response = api_httpx("options", f"{mock_url}/get", timeout=30)
    assert_valid_response(response, "OPTIONS")


def test_invalid_url():
    assert api_httpx("get", "not_a_valid_url", timeout=30) is None


def test_invalid_method(mock_url):
    assert api_httpx("invalid_method", f"{mock_url}/get", timeout=30) is None
