from je_api_testka import test_api_get_json
from je_api_testka import reformat_json


if __name__ == "__main__":
    test_response = test_api_get_json("http://httpbin.org/get")
    print(reformat_json(test_response.get("response_data").get("json_data")))