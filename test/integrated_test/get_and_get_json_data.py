from je_api_testka import test_api_method
from je_api_testka import reformat_json
from je_api_testka import json_element_find

if __name__ == "__main__":
    test_response = test_api_method("get", "https://jsonplaceholder.typicode.com/todos/1")
    print(test_response.get("response_data").get("status_code"))
    print(test_response.get("response_data").get("text"))
    print(reformat_json(test_response.get("response_data").get("text")))
    print(json_element_find(test_response.get("response_data").get("text"), "title"))
