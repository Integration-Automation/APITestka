import sys

from je_api_testka import test_api_method_httpx

if __name__ == "__main__":
    import requests

    test_response = test_api_method_httpx("put", "http://httpbin.org/put", params={"task": "new task"})
    if test_response is not None:
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
    try:
        test_response = test_api_method_httpx("put", "dawdwadaw")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = test_api_method_httpx("http://httpbin.org/get", "put")
    except Exception as error:
        print(repr(error), file=sys.stderr)
