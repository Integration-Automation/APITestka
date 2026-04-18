from je_api_testka import test_api_method_httpx as api_httpx


def test_compare_status_code_pass():
    """result_check_dict with correct status_code should succeed."""
    response = api_httpx(
        "get", "http://httpbin.org/get", result_check_dict={"status_code": 200}, timeout=30
    )
    assert response is not None
    assert response["response_data"]["status_code"] == 200


def test_compare_status_code_fail():
    """result_check_dict with wrong status_code should record error (not raise)."""
    result = api_httpx(
        "get", "http://httpbin.org/get", result_check_dict={"status_code": 300}, timeout=30
    )
    assert result is None
