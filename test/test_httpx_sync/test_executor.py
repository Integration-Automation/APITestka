from je_api_testka import execute_action
from je_api_testka import test_record_instance


def test_execute_single_action():
    """Execute a single GET action via httpx and validate response."""
    test_action_list = [
        ["AT_test_api_method_httpx",
         {"http_method": "get", "test_url": "http://httpbin.org/get", "timeout": 30}]
    ]
    result = execute_action(test_action_list)
    assert isinstance(result, dict)
    for action_response in result.values():
        data = action_response.get("response_data")
        assert data is not None
        assert data.get("start_time") is not None
        assert data.get("end_time") is not None


def test_execute_multiple_actions():
    """Execute multiple POST actions via httpx."""
    test_action_list = [
        ["AT_test_api_method_httpx",
         {"http_method": "post", "test_url": "http://httpbin.org/post",
          "params": {"task": "new task"}, "timeout": 30}],
        ["AT_test_api_method_httpx",
         {"http_method": "post", "test_url": "http://httpbin.org/post", "timeout": 30}],
    ]
    result = execute_action(test_action_list)
    assert isinstance(result, dict)
    assert len(result) == 2


def test_execute_invalid_method():
    """Invalid HTTP methods should be recorded as errors, not crash."""
    test_action_list = [
        ["AT_test_api_method_httpx",
         {"http_method": "invalid_method", "test_url": "http://httpbin.org/post", "timeout": 30}],
    ]
    result = execute_action(test_action_list)
    assert isinstance(result, dict)


def test_execute_records_tracking():
    """Test that executed actions are tracked in test_record_instance."""
    test_action_list = [
        ["AT_test_api_method_httpx",
         {"http_method": "post", "test_url": "http://httpbin.org/post",
          "params": {"task": "new task"}, "timeout": 30}],
    ]
    execute_action(test_action_list)
    assert len(test_record_instance.test_record_list) > 0
    record = test_record_instance.test_record_list[0]
    assert record.get("request_time_sec") is not None
    assert record.get("request_url") is not None
