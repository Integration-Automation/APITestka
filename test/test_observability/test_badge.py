"""Tests for the shields.io endpoint badge."""
from __future__ import annotations

import json

from je_api_testka.utils.generate_report.badge import (
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    generate_badge,
    render_badge,
)
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def test_render_badge_no_data_yellow():
    test_record_instance.clean_record()
    badge = render_badge()
    assert badge["color"] == COLOR_YELLOW


def test_render_badge_all_green():
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({"request_url": "http://x.invalid"})
    badge = render_badge()
    assert badge["color"] == COLOR_GREEN
    test_record_instance.clean_record()


def test_render_badge_some_failures_red():
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({"request_url": "http://a.invalid"})
    test_record_instance.error_record_list.append([{"test_url": "http://b.invalid"}, "boom"])
    badge = render_badge()
    assert badge["color"] == COLOR_RED
    test_record_instance.clean_record()


def test_generate_badge_writes_json(tmp_path):
    target = tmp_path / "badge.json"
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({"request_url": "http://x.invalid"})
    generate_badge(str(target))
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["schemaVersion"] == 1
    test_record_instance.clean_record()
