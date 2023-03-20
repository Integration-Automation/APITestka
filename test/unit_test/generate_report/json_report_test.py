from je_api_testka import generate_json, generate_json_report
from je_api_testka import execute_action
test_action_list = [
    ["test_api_method",
     {"http_method": "get", "test_url": "http://httpbin.org/get",
      "headers": {
          "x-requested-with": "XMLHttpRequest",
          "Content-Type": "application/x-www-form-urlencoded",
          "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
      }
      }
     ],
    ["test_api_method",
     {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
      "result_check_dict": {"status_code": 200}
      }
     ],
    ["test_api_method",
     {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
      "result_check_dict": {"status_code": 300}
      }
     ]
]
execute_action(test_action_list)
generate_json()
generate_json_report()
