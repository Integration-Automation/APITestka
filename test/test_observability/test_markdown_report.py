"""Tests for markdown report renderer."""
from __future__ import annotations

from je_api_testka.utils.generate_report.markdown_report import (
    generate_markdown_report,
    render_markdown,
)
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def test_render_markdown_includes_counts():
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({
        "request_method": "GET",
        "request_url": "http://x.invalid",
        "status_code": 200,
        "request_time_sec": 0.05,
    })
    test_record_instance.error_record_list.append([
        {"http_method": "POST", "test_url": "http://y.invalid"}, "boom",
    ])
    md = render_markdown()
    assert "**Successes:** 1" in md
    assert "**Failures:** 1" in md
    assert "## Successful requests" in md
    assert "## Failed requests" in md
    assert "boom" in md
    test_record_instance.clean_record()


def test_generate_markdown_report_writes_file(tmp_path):
    test_record_instance.clean_record()
    target = tmp_path / "report.md"
    generate_markdown_report(str(target))
    assert target.exists()
    assert "APITestka Report" in target.read_text(encoding="utf-8")
