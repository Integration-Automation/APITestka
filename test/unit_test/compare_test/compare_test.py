import sys

from je_api_testka import test_api_method

test_response = test_api_method("get", "http://httpbin.org/get", result_check_dict={"status_code": "200"})
if test_response is not None:
    print(test_response.get("response_data").get("status_code"))

# will raise exception because result_check_dict status_code not 300
try:
    test_response = test_api_method("get", "http://httpbin.org/get", result_check_dict={"status_code": "300"})
except Exception as error:
    print(repr(error), file=sys.stderr)
