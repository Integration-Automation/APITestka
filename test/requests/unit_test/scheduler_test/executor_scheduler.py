from je_api_testka import execute_action

execute_action([
    ["AT_scheduler_event_trigger", {
        "function": "AT_test_api_method", "wait_value": 5, "scheduler_type": "blocking",
        "kwargs": {"http_method": "get", "test_url": "http://google.com"}
    }],
    ["AT_start_blocking_scheduler"]
])
