from je_api_testka import test_api_get
from je_api_testka import test_api_get_json

test_response = test_api_get("http://httpbin.org/get")
print(test_response.get("response_data").get("status_code"))
test_response = test_api_get_json("http://httpbin.org/get")
print(test_response.get("response_data").get("status_code"))
print(test_response.get("response_data").get("json_data"))
test_response = test_api_get("http://httpbin.org")
print(test_response.get("response_data").get("status_code"))
print(test_response.get("response_data").get("text"))
print(test_response.get("response_data").get("elapsed"))
