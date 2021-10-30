from je_api_test import test_api_delete

test_response = test_api_delete("http://httpbin.org/delete")
print(test_response.get("response_data").get("status_code"))
