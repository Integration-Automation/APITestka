def test_report_generation_requests(run_report_suite):
    """Verify all report flavors using the requests backend."""
    run_report_suite("AT_test_api_method")
