import os

from je_api_testka import execute_action, generate_html, generate_html_report
from je_api_testka import generate_json, generate_json_report
from je_api_testka import generate_xml, generate_xml_report


def _run_test_actions():
    """Run httpx actions that produce both success and failure records."""
    test_action_list = [
        ["AT_test_api_method_httpx", {
            "http_method": "get", "test_url": "http://httpbin.org/get",
            "result_check_dict": {"status_code": 200},
            "timeout": 30,
        }],
        ["AT_test_api_method_httpx", {
            "http_method": "post", "test_url": "http://httpbin.org/post",
            "params": {"task": "new task"},
            "result_check_dict": {"status_code": 300},
            "timeout": 30,
        }],
    ]
    execute_action(test_action_list)


def test_generate_html():
    _run_test_actions()
    success_list, failure_list = generate_html()
    assert isinstance(success_list, list)
    assert isinstance(failure_list, list)
    assert len(success_list) > 0


def test_generate_html_report(tmp_path):
    _run_test_actions()
    report_path = str(tmp_path / "test_report")
    generate_html_report(report_path)
    assert os.path.exists(report_path + ".html")


def test_generate_json():
    _run_test_actions()
    success_dict, failure_dict = generate_json()
    assert isinstance(success_dict, dict)
    assert isinstance(failure_dict, dict)
    assert len(success_dict) > 0


def test_generate_json_report(tmp_path):
    _run_test_actions()
    report_path = str(tmp_path / "test_report")
    generate_json_report(report_path)
    assert os.path.exists(report_path + "_success.json")
    assert os.path.exists(report_path + "_failure.json")


def test_generate_xml():
    _run_test_actions()
    success_xml, failure_xml = generate_xml()
    assert isinstance(success_xml, str)
    assert isinstance(failure_xml, str)
    assert "<xml_data>" in success_xml


def test_generate_xml_report(tmp_path):
    _run_test_actions()
    report_path = str(tmp_path / "test_report")
    generate_xml_report(report_path)
    assert os.path.exists(report_path + "_success.xml")
    assert os.path.exists(report_path + "_failure.xml")
