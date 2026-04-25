def test_report_generation_httpx_async(run_report_suite):
    """Verify all report flavors using the async httpx backend (via delegate)."""
    run_report_suite("AT_delegate_async_httpx")
