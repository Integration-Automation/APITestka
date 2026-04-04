from je_api_testka import test_api_method_httpx_async as api_httpx_async


async def test_compare_status_code_pass():
    """result_check_dict with correct status_code should succeed."""
    response = await api_httpx_async(
        "get", "http://httpbin.org/get", result_check_dict={"status_code": 200}
    )
    assert response is not None
    assert response["response_data"]["status_code"] == 200


async def test_compare_status_code_fail():
    """result_check_dict with wrong status_code should record error (not raise)."""
    result = await api_httpx_async(
        "get", "http://httpbin.org/get", result_check_dict={"status_code": 300}
    )
    assert result is None
