"""
JUnit XML report generator for CI integration (GitHub Actions, Jenkins, etc).
"""
from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement

from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_JUNIT_FILENAME: str = "apitestka_junit.xml"
DEFAULT_TEST_SUITE_NAME: str = "APITestka"


def generate_junit_report(file_name: str = DEFAULT_JUNIT_FILENAME,
                          suite_name: str = DEFAULT_TEST_SUITE_NAME) -> Path:
    """Write the global test record into a JUnit XML file and return its path."""
    apitestka_logger.info(
        f"junit_report.py generate_junit_report file_name: {file_name} suite_name: {suite_name}"
    )
    success_records = list(test_record_instance.test_record_list)
    failure_records = list(test_record_instance.error_record_list)
    total = len(success_records) + len(failure_records)

    suite = Element(
        "testsuite",
        attrib={
            "name": suite_name,
            "tests": str(total),
            "failures": str(len(failure_records)),
            "errors": "0",
        },
    )
    for index, record in enumerate(success_records, start=1):
        case = SubElement(
            suite,
            "testcase",
            attrib={
                "classname": suite_name,
                "name": str(record.get("request_url") or f"success_{index}"),
                "time": str(record.get("request_time_sec") or 0),
            },
        )
        SubElement(case, "system-out").text = str(record.get("status_code"))
    for index, record in enumerate(failure_records, start=1):
        meta = record[0] if record and isinstance(record[0], dict) else {}
        message = record[1] if len(record) > 1 else ""
        case = SubElement(
            suite,
            "testcase",
            attrib={
                "classname": suite_name,
                "name": str(meta.get("test_url") or f"failure_{index}"),
                "time": "0",
            },
        )
        SubElement(case, "failure", attrib={"message": str(message)}).text = str(meta)

    output = Path(file_name)
    ElementTree(suite).write(output, encoding="utf-8", xml_declaration=True)
    return output
