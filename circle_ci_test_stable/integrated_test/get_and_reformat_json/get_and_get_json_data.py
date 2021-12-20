from je_api_testka import json_element_find
from je_api_testka import reformat_json
from je_api_testka import test_api_method

if __name__ == "__main__":
    import requests

    test_response = test_api_method("get", "https://jsonplaceholder.typicode.com/todos/1")
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("text"))
    print(reformat_json(test_response.get("response_data").get("text")))
    print(json_element_find(test_response.get("response_data").get("text"), "title"))
    try:
        test_response = test_api_method("get", "wadwaddawdwa")
    except requests.exceptions.MissingSchema as error:
        print(repr(error))
    from je_api_testka import APITesterException

    try:
        test_response = test_api_method("dwadadwawd", "get")
    except APITesterException as error:
        print(repr(error))
