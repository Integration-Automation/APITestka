from je_api_testka import test_api_head

test_response = test_api_head("http://httpbin.org/get")
print(test_response.get("response_data").get("status_code"))
