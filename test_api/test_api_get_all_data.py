from je_api_testka import test_api_get

test_response = test_api_get("http://httpbin.org")
print(test_response)
print(test_response.get("response_data"))
