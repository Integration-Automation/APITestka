from je_api_testka import callback_executor

print(
    callback_executor.callback_function(
        trigger_function_name="test_api_method",
        callback_function=print,
        callback_param_method=None,
        callback_function_param=None,
        **{
            "http_method": "post", "test_url": "http://httpbin.org/post",
            "params": {"task": "new task"},
            "result_check_dict": {
                "status_code": 200
            }
        }
    )
)
