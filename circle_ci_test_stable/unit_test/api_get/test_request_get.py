import sys

from je_api_testka import test_api_method

if __name__ == "__main__":
    import requests

    test_response = test_api_method("get", "http://httpbin.org/get")
    print(test_response.get("response_data"))
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("text"))
    print(test_response.get("response_data").get("headers"))
    print(test_response.get("response_data").get("content"))
    print(test_response.get("response_data").get("history"))
    print(test_response.get("response_data").get("encoding"))
    print(test_response.get("response_data").get("cookies"))
    print(test_response.get("response_data").get("elapsed"))
    print(test_response.get("response_data").get("request_method"))
    print(test_response.get("response_data").get("request_url"))
    print(test_response.get("response_data").get("request_body"))
    test_response = test_api_method("get", "http://httpbin.org/get", get_json=True)
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("json_data"))
    try:
        test_response = test_api_method("get", "dawdwadaw")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)
    from je_api_testka import APITesterException

    try:
        test_response = test_api_method("http://httpbin.org/get", "get")
    except APITesterException as error:
        print(repr(error), file=sys.stderr)