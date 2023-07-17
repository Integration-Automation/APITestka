from je_api_testka import execute_action

execute_action(
    [
        ["AT_test_api_method", {
            "http_method": "get",
            "test_url": "http://localhost:8090/test",
            "result_check_dict": {"status_code": 200}
        }],
        ["AT_test_api_method", {
            "http_method": "post",
            "test_url": "http://localhost:8090/test",
            "result_check_dict": {"status_code": 200}
        }]
    ]
)
