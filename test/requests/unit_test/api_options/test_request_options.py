import sys

from je_api_testka import test_api_method_requests

if __name__ == "__main__":
    import requests

    test_response = test_api_method_requests("options", "http://httpbin.org/get")
    if test_response is not None:
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("elapsed"))
    try:
        test_response = test_api_method_requests("options", "dawdwadaw")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = test_api_method_requests("http://httpbin.org/get", "options")
    except Exception as error:
        print(repr(error), file=sys.stderr)
