from je_api_test.requests_wrapper.requests_wrapper import api_tester_method


def test_api_get(test_url, **kwargs):
    response = api_tester_method("get", test_url=test_url, **kwargs)
    response_data = {
        "status_code": response.status_code,
        "text": response.text,
        "content": response.content,
        "headers": response.headers,
        "history": response.history,
        "encoding": response.encoding,
        "cookies": response.cookies,
        "elapsed": response.elapsed,
        "reason": response.reason,
        "url": response.url,
        "is_redirect": response.is_redirect
    }

    return response_data


def test_api_get_json(test_url, **kwargs):
    response = api_tester_method("get", test_url=test_url, **kwargs)
    response_data = {
        "status_code": response.status_code,
        "json_data": response.json()
    }
    return response_data


if __name__ == "__main__":
    print(test_api_get("http://localhost:5000/tasks").get("status_code"))
    print(test_api_get_json("http://localhost:5000/tasks").get("json_data"))
