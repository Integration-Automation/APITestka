from je_api_testka import test_api_patch

test_response = test_api_patch("http://httpbin.org/patch", params={"task": "new task"})
print(test_response.get("response_data").get("status_code"))
