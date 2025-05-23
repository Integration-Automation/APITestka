import sys

import requests.exceptions

from je_api_testka import generate_html
from je_api_testka import test_api_method_requests

if __name__ == "__main__":
    test_response = test_api_method_requests("delete", "http://httpbin.org/delete")
    if test_response is not None:
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
        print(test_response.get("response_data").get("elapsed"))
        print(test_response.get("response_data").get("elapsed").total_seconds())
        print(test_response.get("response_data").get("request_time_sec"))
    try:
        test_response = test_api_method_requests("delete", "wadwaddawdwa")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)
    try:
        test_response = test_api_method_requests("dwadadwawd", "delete")
    except Exception as error:
        print(repr(error), file=sys.stderr)

generate_html()
