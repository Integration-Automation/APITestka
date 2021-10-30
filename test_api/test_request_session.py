from je_api_test import test_api_session

test_response = test_api_session("http://httpbin.org/get")
print(test_response.get("response_data").get("status_code"))
