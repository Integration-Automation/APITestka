"""Tests for the terminal summary printer."""
from __future__ import annotations

from je_api_testka.cli.tui_summary import render_terminal_summary
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def test_summary_includes_counts():
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({"request_url": "https://x.invalid"})
    test_record_instance.error_record_list.append([{"test_url": "https://y.invalid"}, "boom"])
    output = render_terminal_summary()
    assert "OK    1" in output
    assert "FAIL  1" in output
    assert "boom" in output
    test_record_instance.clean_record()
