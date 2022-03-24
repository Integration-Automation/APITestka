import sys

from je_api_testka import test_api_method

if __name__ == "__main__":
    import requests

    test_response = test_api_method("options", "http://httpbin.org/get")
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("elapsed"))
    try:
        test_response = test_api_method("options", "dawdwadaw")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = test_api_method("http://httpbin.org/get", "options")
    except Exception as error:
        print(repr(error), file=sys.stderr)
