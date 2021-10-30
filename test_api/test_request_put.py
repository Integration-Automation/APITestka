from je_api_test import test_api_put

test_response = test_api_put("http://httpbin.org/put", params={"task": "new task"})
print(test_response.get("response_data").get("status_code"))
