from je_api_test.requests_wrapper.requests_wrapper import api_tester_method

from je_api_test.utils.api_test_exceptions import APITesterPutException

from je_api_test.utils.get_api_data import get_api_response_data


def test_api_put(test_url, **kwargs):
    try:
        response = api_tester_method("put", test_url=test_url, **kwargs)
    except APITesterPutException:
        raise APITesterPutException
    try:
        response_data = get_api_response_data(response)
    except APITesterGetDataException:
        raise APITesterGetDataException
    return {"response": response, "response_data": response_data}


if __name__ == "__main__":
    test_response = test_api_put("http://localhost:5000/tasks/task3", params={"task": "new task"}).get("response_data")
    print(test_response.get("status_code"))
    print(test_response.get("headers"))

