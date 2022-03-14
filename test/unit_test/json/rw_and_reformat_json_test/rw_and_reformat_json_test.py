import json
import os

from je_api_testka import read_action_json
from je_api_testka import write_action_json
from je_api_testka import reformat_json


test_list = [
    ("get", "http://httpbin.org/get", False, {"headers": {
        'x-requested-with': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    }}),
    ("post", "http://httpbin.org/post", False, {"params": {"task": "new task"}})
]
test_dumps_json = json.dumps(test_list)
print(test_dumps_json)
test_loads_json = json.loads(test_dumps_json)
print(test_loads_json)
list(test_loads_json)

write_action_json(os.getcwd() + "/test.json", test_dumps_json)
read_json = reformat_json(read_action_json(os.getcwd() + "/test.json"))
print(read_json)
list(read_json)
print(read_json)
