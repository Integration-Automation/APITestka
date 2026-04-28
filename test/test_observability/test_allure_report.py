"""Tests for the Allure JSON report."""
from __future__ import annotations

import json

from je_api_testka.utils.generate_report.allure_report import generate_allure_report
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def test_generate_allure_report_writes_files(tmp_path):
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({
        "request_url": "https://example.invalid/get",
        "request_method": "GET",
        "status_code": 200,
    })
    test_record_instance.error_record_list.append([
        {"test_url": "https://example.invalid/x"},
        "boom",
    ])

    written = generate_allure_report(str(tmp_path))
    assert len(written) == 2
    statuses = []
    for path in written:
        payload = json.loads(path.read_text(encoding="utf-8"))
        statuses.append(payload["status"])
    assert sorted(statuses) == ["failed", "passed"]
    test_record_instance.clean_record()
