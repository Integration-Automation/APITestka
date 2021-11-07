from je_api_testka import test_api_method

if __name__ == "__main__":
    test_response = test_api_method("head", "http://httpbin.org/get")
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("elapsed"))
