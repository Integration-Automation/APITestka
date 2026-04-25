from je_api_testka import test_api_method_requests as api_requests


def test_get(mock_url, assert_valid_response, assert_get_extras):
    response = api_requests("get", f"{mock_url}/get", timeout=30)
    assert_valid_response(response, "GET")
    assert_get_extras(response)


def test_post(mock_url, assert_valid_response):
    response = api_requests("post", f"{mock_url}/post", params={"task": "new task"}, timeout=30)
    assert_valid_response(response, "POST")


def test_put(mock_url, assert_valid_response):
    response = api_requests("put", f"{mock_url}/put", params={"task": "new task"}, timeout=30)
    assert_valid_response(response, "PUT")


def test_patch(mock_url, assert_valid_response):
    response = api_requests("patch", f"{mock_url}/patch", params={"task": "new task"}, timeout=30)
    assert_valid_response(response, "PATCH")


def test_delete(mock_url, assert_valid_response):
    response = api_requests("delete", f"{mock_url}/delete", timeout=30)
    assert_valid_response(response, "DELETE")
    assert response["response_data"].get("request_time_sec") >= 0


def test_head(mock_url, assert_valid_response):
    response = api_requests("head", f"{mock_url}/get", headers={
        "x-requested-with": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    }, timeout=30)
    assert_valid_response(response, "HEAD")


def test_options(mock_url, assert_valid_response):
    response = api_requests("options", f"{mock_url}/get", timeout=30)
    assert_valid_response(response, "OPTIONS")


def test_session_get(mock_url, assert_valid_response):
    response = api_requests("session_get", f"{mock_url}/get", timeout=30)
    assert_valid_response(response, "GET")


def test_invalid_url():
    assert api_requests("get", "not_a_valid_url", timeout=30) is None


def test_invalid_method(mock_url):
    assert api_requests("invalid_method", f"{mock_url}/get", timeout=30) is None
