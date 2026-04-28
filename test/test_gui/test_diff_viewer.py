"""Tests for the side-by-side diff renderer."""
from __future__ import annotations

from je_api_testka.gui.diff_viewer import render_side_by_side


def test_identical_payload_says_identical():
    rendered = render_side_by_side({"a": 1}, {"a": 1})
    assert "(identical)" in rendered


def test_changes_appear_with_marker():
    rendered = render_side_by_side({"a": 1}, {"a": 2})
    assert "~ a" in rendered
    assert "1" in rendered and "2" in rendered


def test_added_and_removed_marked():
    rendered = render_side_by_side({"a": 1}, {"b": 1})
    assert "- a" in rendered
    assert "+ b" in rendered
