def test_report_generation_httpx_sync(run_report_suite):
    """Verify all report flavors using the sync httpx backend."""
    run_report_suite("AT_test_api_method_httpx")
