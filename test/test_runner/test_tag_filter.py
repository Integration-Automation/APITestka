"""Tests for the tag filter."""
from __future__ import annotations

from je_api_testka.runner.tag_filter import filter_actions_by_tag


def test_no_tags_returns_all():
    actions = [["AT_x", {"tags": ["smoke"]}], ["AT_y", {"tags": ["regression"]}]]
    assert filter_actions_by_tag(actions, []) == actions


def test_keeps_overlapping_tags():
    actions = [
        ["AT_a", {"tags": ["smoke"]}],
        ["AT_b", {"tags": ["regression"]}],
        ["AT_c", {"tags": ["smoke", "p0"]}],
    ]
    filtered = filter_actions_by_tag(actions, {"smoke"})
    assert len(filtered) == 2
    assert filtered[0][0] == "AT_a"


def test_untagged_excluded_by_default():
    actions = [["AT_a", {}], ["AT_b", {"tags": ["smoke"]}]]
    filtered = filter_actions_by_tag(actions, {"smoke"})
    assert len(filtered) == 1


def test_include_untagged_keeps_them():
    actions = [["AT_a", {}], ["AT_b", {"tags": ["smoke"]}]]
    filtered = filter_actions_by_tag(actions, {"smoke"}, include_untagged=True)
    assert len(filtered) == 2
