import json
import sys

from je_api_testka import APITesterException
from je_api_testka import reformat_json
from je_api_testka import test_api_method

if __name__ == "__main__":
    test_response = test_api_method("get", "http://httpbin.org/get", get_json=True)
    print(reformat_json(test_response.get("response_data").get("json_data")))
    test_json_string = '[["get", "http://httpbin.org/get", false, {"headers": {"x-requested-with": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded", "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"}}], ["post", "http://httpbin.org/post", false, {"params": {"task": "new task"}}]]'
    print(reformat_json(test_json_string))
    try:
        test_json = "dwadwjawdkwjadlkwjadlkjwadlkjdwa"
        print(reformat_json(test_json))
    except json.JSONDecodeError as error:
        print(repr(error), file=sys.stderr)
    try:
        test_json = ("{90}{DW]dadw[dladwkadodkawokdwadwadaw}")
        print(reformat_json(test_json))
    except json.JSONDecodeError as error:
        print(repr(error), file=sys.stderr)
    try:
        test_json = {("{90}{DW]dadw[dladwkadodkawokdwadwadaw}")}
        print(reformat_json(test_json))
    except APITesterException as error:
        print(repr(error), file=sys.stderr)
    try:
        test_fstring = "dwadaw6d54wa65d46wa54d6w5a4d5w6a4dw56a4d65aw41d23.wsa51d453aw64ythgnbmgjnuki]"
        test_json = f"{test_fstring}"
        print(reformat_json(test_json))
    except json.JSONDecodeError as error:
        print(repr(error), file=sys.stderr)
