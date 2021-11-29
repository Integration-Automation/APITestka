from je_api_testka import test_api_method
from je_api_testka import reformat_json

from json import dumps


if __name__ == "__main__":
    test_response = test_api_method("get", "http://httpbin.org/get", get_json=True)
    print(reformat_json(test_response.get("response_data").get("json_data")))
