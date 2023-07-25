import sys

from je_api_testka import test_api_method_httpx

if __name__ == "__main__":
    import requests

    test_response = test_api_method_httpx("get", "http://httpbin.org")
    if test_response is not None:
        print(test_response)
        print(test_response.get("response_data"))
    try:
        test_response = test_api_method_httpx("get", "wadwaddawdwa")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = test_api_method_httpx("dwadadwawd", "get")
    except Exception as error:
        print(repr(error), file=sys.stderr)
