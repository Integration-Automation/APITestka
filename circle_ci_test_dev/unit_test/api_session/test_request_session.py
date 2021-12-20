import sys

from je_api_testka import test_api_method

if __name__ == "__main__":
    import requests

    test_response = test_api_method("session_get", "http://httpbin.org/get")
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("text"))
    try:
        test_response = test_api_method("session_get", "dawdwadaw")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)
    from je_api_testka import APITesterException

    try:
        test_response = test_api_method("http://httpbin.org/get", "session_get")
    except APITesterException as error:
        print(repr(error), file=sys.stderr)
