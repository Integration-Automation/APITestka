from je_api_testka import callback_executor


def test_callback_with_trigger():
    """Execute a trigger function with a callback."""
    callback_called = []

    def my_callback():
        callback_called.append(True)

    result = callback_executor.callback_function(
        trigger_function_name="AT_test_api_method",
        callback_function=my_callback,
        callback_param_method=None,
        callback_function_param=None,
        **{
            "http_method": "post",
            "test_url": "http://127.0.0.1:8091/post",
            "params": {"task": "new task"},
            "result_check_dict": {"status_code": 200},
            "timeout": 30,
        }
    )
    assert result is not None
    assert len(callback_called) == 1
