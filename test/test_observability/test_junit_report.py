"""Tests for the JUnit XML report."""
from __future__ import annotations

from xml.etree import ElementTree

from je_api_testka.utils.generate_report.junit_report import generate_junit_report
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def test_generate_junit_report_writes_expected_xml(tmp_path):
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({
        "request_url": "http://example.invalid/get",
        "request_time_sec": 0.1,
        "status_code": 200,
    })
    test_record_instance.error_record_list.append([
        {"test_url": "http://example.invalid/missing"},
        "boom",
    ])

    target = tmp_path / "junit.xml"
    generate_junit_report(str(target))

    tree = ElementTree.parse(target)
    suite = tree.getroot()
    assert suite.tag == "testsuite"
    assert suite.attrib["tests"] == "2"
    assert suite.attrib["failures"] == "1"
    failure = suite.find("./testcase/failure")
    assert failure is not None
    test_record_instance.clean_record()
