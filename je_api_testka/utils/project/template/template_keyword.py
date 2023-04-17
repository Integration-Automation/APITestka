template_keyword_1: list = [
    ["test_api_method",
     {
         "http_method": "post",
         "test_url": "http://httpbin.org/post",
         "params": {"task": "new task"},
         "result_check_dict": {"status_code": 200}
     }
     ]
]

template_keyword_2: list = [
    ["test_api_method",
     {
         "http_method": "get",
         "test_url": "http://httpbin.org/post",
         "result_check_dict": {"status_code": 405}
     }
     ]
]

bad_template_1 = [
    ["add_package_to_executor", ["os"]],
    ["os_system", ["python --version"]],
    ["os_system", ["python -m pip --version"]],
]
