import sys

from je_api_testka import test_api_method


if __name__ == "__main__":
    import requests

    test_response = test_api_method("get", "http://httpbin.org")
    print(test_response)
    print(test_response.get("response_data"))
    try:
        test_response = test_api_method("get", "wadwaddawdwa")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)
    from je_api_testka import APITesterException

    try:
        test_response = test_api_method("dwadadwawd", "get")
    except APITesterException as error:
        print(repr(error), file=sys.stderr)
