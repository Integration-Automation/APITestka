from je_api_testka import test_api_method

if __name__ == "__main__":
    test_response = test_api_method("delete", "http://httpbin.org/delete")
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("text"))
    print(test_response.get("response_data").get("elapsed"))
