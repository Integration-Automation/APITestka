from je_api_testka import test_api_method_requests as api_requests


def test_compare_status_code_pass():
    """result_check_dict with correct status_code should succeed."""
    response = api_requests(
        "get", "http://httpbin.org/get", result_check_dict={"status_code": 200}, timeout=30
    )
    assert response is not None
    assert response["response_data"]["status_code"] == 200


def test_compare_status_code_fail():
    """result_check_dict with wrong status_code should record error (not raise)."""
    result = api_requests(
        "get", "http://httpbin.org/get", result_check_dict={"status_code": 300}, timeout=30
    )
    # The function catches the exception internally and returns None
    assert result is None
