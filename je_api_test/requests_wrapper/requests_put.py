from requests import put


def test_api_put(test_url, data, **kwargs):
    if kwargs is None:
        response = put(test_url, data)
    else:
        response = put(test_url, data, **kwargs)
    response_data = {
        "status_code": response.status_code,
        "text": response.text,
        "content": response.content,
        "headers": response.headers,
        "history": response.history,
        "encoding": response.encoding,
        "cookies": response.cookies,
        "elapsed": response.elapsed
    }
    return response_data


if __name__ == "__main__":
    print(test_api_put("http://localhost:5000/tasks/task3", {"task": "new task"}).get("status_code"))

