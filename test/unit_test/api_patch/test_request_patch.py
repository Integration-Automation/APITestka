import sys

from je_api_testka import test_api_method

if __name__ == "__main__":
    import requests

    test_response = test_api_method("patch", "http://httpbin.org/patch", params={"task": "new task"})
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("text"))
    try:
        test_response = test_api_method("patch", "dawdwadaw")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)
    from je_api_testka import APITesterException

    try:
        test_response = test_api_method("http://httpbin.org/get", "patch")
    except Exception as error:
        print(repr(error), file=sys.stderr)
