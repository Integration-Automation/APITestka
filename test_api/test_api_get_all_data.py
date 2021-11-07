from je_api_testka import test_api_method

if __name__ == "__main__":
    test_response = test_api_method("get", "http://httpbin.org")
    print(test_response)
    print(test_response.get("response_data"))
