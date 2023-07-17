import os

from je_api_testka import read_action_json
from je_api_testka import reformat_json
from je_api_testka import write_action_json

test_list = \
    [
        ["AT_test_api_method",
         {"http_method": "get", "test_url": "http://httpbin.org/get",
          "headers": {
              'x-requested-with': 'XMLHttpRequest',
              'Content-Type': 'application/x-www-form-urlencoded',
              'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
          }
          }
         ],
        ["AT_test_api_method",
         {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
          "result_check_dict": {"status_code": 200}
          }
         ]
    ]

write_action_json(os.getcwd() + "/test1.json", test_list)
read_json = reformat_json(read_action_json(os.getcwd() + "/test1.json"))
print(read_json)
