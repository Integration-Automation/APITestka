from je_api_testka import execute_action

execute_action([
    ["scheduler_event_trigger", {
        "function": "test_api_method", "wait_value": 5, "scheduler_type": "blocking",
        "kwargs": {"http_method": "get", "test_url": "http://google.com"}
    }],
    ["start_blocking_scheduler"]
])
