"""The HTML, JSON and XML reports are written as UTF-8 and survive text outside cp950."""
import json
from pathlib import Path

import pytest

from je_api_testka.utils.generate_report.html_report_generate import generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json_report
from je_api_testka.utils.generate_report.xml_report import generate_xml_report
from je_api_testka.utils.test_record.test_record_class import test_record_instance

_TEXT = "回應 😀"  # the emoji is outside cp950, the zh-TW Windows locale encoding


def _record(text=_TEXT, content=None):
    return {
        "status_code": 200, "text": text, "content": content if content is not None else text.encode("utf-8"),
        "headers": {}, "history": [], "encoding": "utf-8", "cookies": {}, "elapsed": 0.1,
        "request_time_sec": 0.1, "request_method": "GET", "request_url": "https://example.test/",
        "request_body": None, "start_time": "s", "end_time": "e",
    }


@pytest.fixture
def one_record():
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append(_record())
    yield
    test_record_instance.clean_record()


@pytest.mark.parametrize("generate, suffix", [
    (generate_html_report, ".html"),
    (generate_xml_report, "_success.xml"),
], ids=["html", "xml"])
def test_text_report_is_utf8(tmp_path, one_record, generate, suffix):
    base = str(tmp_path / "report")
    generate(base)
    assert _TEXT in Path(base + suffix).read_bytes().decode("utf-8")


def test_json_report_keeps_the_text(tmp_path, one_record):
    base = str(tmp_path / "report")
    generate_json_report(base)
    written = json.loads(Path(base + "_success.json").read_bytes().decode("utf-8"))
    assert written["Success_Test1"]["text"] == _TEXT


_SCRIPT = "<script>alert(1)</script>"


def test_html_report_escapes_response_and_error_text(tmp_path):
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append(_record(text=_SCRIPT, content=_SCRIPT.encode("utf-8")))
    test_record_instance.error_record_list.append([
        {"http_method": "get", "test_url": f"https://example.test/?q={_SCRIPT}"}, ValueError(_SCRIPT)])
    try:
        base = str(tmp_path / "report")
        generate_html_report(base)
        written = Path(base + ".html").read_text(encoding="utf-8")
    finally:
        test_record_instance.clean_record()
    assert _SCRIPT not in written
    assert written.count("&lt;script&gt;alert(1)&lt;/script&gt;") == 4


def test_html_report_survives_binary_content(tmp_path):
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append(_record(text="bin", content=b"\xff\xfe\x00png"))
    try:
        base = str(tmp_path / "report")
        generate_html_report(base)
        assert "�" in Path(base + ".html").read_text(encoding="utf-8")
    finally:
        test_record_instance.clean_record()
