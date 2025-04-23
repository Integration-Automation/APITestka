import sys

from je_api_testka import test_api_method_requests

if __name__ == "__main__":
    import requests
    import sys

    sys.stdout.encoding = 'utf-8'

    test_response = test_api_method_requests("get", "http://httpbin.org")
    if test_response is not None:
        print(test_response)
        print(test_response.get("response_data"))
    try:
        test_response = test_api_method_requests("get", "wadwaddawdwa")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = test_api_method_requests("dwadadwawd", "get")
    except Exception as error:
        print(repr(error), file=sys.stderr)
