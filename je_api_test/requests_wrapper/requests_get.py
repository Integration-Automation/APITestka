from je_api_test.requests_wrapper.requests_wrapper import api_tester_method

from je_api_test.utils.api_test_exceptions import APITesterGetJsonException
from je_api_test.utils.api_test_exceptions import APITesterGetException
from je_api_test.utils.api_test_exceptions import APITesterGetDataException
from je_api_test.utils.get_api_data import get_api_response_data


def test_api_get(test_url, **kwargs):
    try:
        response = api_tester_method("get", test_url=test_url, **kwargs)
    except APITesterGetException:
        raise APITesterGetException
    try:
        response_data = get_api_response_data(response)
    except APITesterGetDataException:
        raise APITesterGetDataException

    return {"response": response, "response_data": response_data}


def test_api_get_json(test_url, **kwargs):
    try:
        response = api_tester_method("get", test_url=test_url, **kwargs)
    except APITesterGetException:
        raise APITesterGetException
    try:
        response_data = {
            "status_code": response.status_code,
            "json_data": response.json()
        }
    except APITesterGetJsonException:
        raise APITesterGetJsonException
    return {"response": response, "response_data": response_data}


if __name__ == "__main__":
    print(test_api_get("http://localhost:5000/tasks").get("response_data").get("status_code"))
    print(test_api_get_json("http://localhost:5000/tasks").get("response_data").get("json_data"))
