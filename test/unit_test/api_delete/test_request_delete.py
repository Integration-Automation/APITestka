import sys

import requests.exceptions

from je_api_testka import test_api_method

if __name__ == "__main__":
    test_response = test_api_method("delete", "http://httpbin.org/delete")
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("text"))
    print(test_response.get("response_data").get("elapsed"))
    print(test_response.get("response_data").get("elapsed").total_seconds())
    print(test_response.get("response_data").get("request_time_sec"))
    try:
        test_response = test_api_method("delete", "wadwaddawdwa")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)
    from je_api_testka import APITesterException

    try:
        test_response = test_api_method("dwadadwawd", "delete")
    except APITesterException as error:
        print(repr(error), file=sys.stderr)
