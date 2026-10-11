"""Tests for Pact v2 matching rules."""
from __future__ import annotations

from je_api_testka.contract.matching import body_mismatches, header_mismatches, json_type

TYPE = {"$.body": {"match": "type"}}


def test_equality_without_rules():
    assert body_mismatches({"id": 1}, {"id": 1, "extra": True}) == []
    assert body_mismatches({"id": 1}, {"id": 2}) == ["$.body.id: expected 1, got 2"]
    assert body_mismatches({"id": 1}, {}) == ["$.body.id: missing"]


def test_true_is_not_one():
    assert body_mismatches({"flag": 1}, {"flag": True})


def test_type_rule_cascades():
    assert body_mismatches({"id": 1, "name": "a", "price": 1.5}, {"id": 7, "name": "b", "price": 3}, TYPE) == []
    assert body_mismatches({"id": 1}, {"id": "7"}, TYPE) == ["$.body.id: expected a number, got string '7'"]


def test_type_rule_on_arrays_uses_first_element():
    expected = {"items": [{"id": 1}]}
    assert body_mismatches(expected, {"items": [{"id": 2}, {"id": 3}]}, TYPE) == []
    assert body_mismatches(expected, {"items": []}, TYPE) == []
    assert body_mismatches(expected, {"items": [{"id": "x"}]}, TYPE) == [
        "$.body.items[0].id: expected a number, got string 'x'"]


def test_min_rule_on_array():
    rules = {"$.body.items": {"match": "type", "min": 1}}
    assert body_mismatches({"items": [1]}, {"items": []}, rules) == ["$.body.items: expected at least 1 items, got 0"]


def test_equality_arrays_compare_length_and_items():
    assert body_mismatches([1, 2], [1, 2, 3]) == ["$.body: expected 2 items, got 3"]
    assert body_mismatches([1, 2], [1, 3]) == ["$.body[1]: expected 2, got 3"]


def test_regex_and_wildcards_and_specific_rule_wins():
    rules = {
        "$.body": {"match": "type"},
        "$.body.items[*].sku": {"match": "regex", "regex": "[A-Z]{3}-\\d+"},
        "$.body.code": {"match": "regex", "regex": "\\d{3}"},
    }
    expected = {"code": "200", "items": [{"sku": "ABC-1"}]}
    assert body_mismatches(expected, {"code": "404", "items": [{"sku": "XYZ-99"}]}, rules) == []
    assert body_mismatches(expected, {"code": "4O4", "items": [{"sku": "bad"}]}, rules) == [
        "$.body.code: '4O4' does not match /\\d{3}/",
        "$.body.items[0].sku: 'bad' does not match /[A-Z]{3}-\\d+/",
    ]


def test_structure_mismatches():
    assert body_mismatches({"a": 1}, [1]) == ["$.body: expected an object, got array"]
    assert body_mismatches([1], {"a": 1}) == ["$.body: expected an array, got object"]


def test_headers():
    actual = {"content-type": "application/json; charset=utf-8", "X-Id": "abc-123"}
    assert header_mismatches({"Content-Type": "application/json"}, actual) == []
    assert header_mismatches({"X-Id": "abc-124"}, actual) == ["$.headers.X-Id: expected 'abc-124', got 'abc-123'"]
    assert header_mismatches({"X-Id": "x"}, actual, {"$.headers.X-Id": {"match": "regex", "regex": "abc-\\d+"}}) == []
    assert header_mismatches({"X-Missing": "x"}, actual) == ["$.headers.X-Missing: missing"]
    assert header_mismatches({"Content-Type": "text/plain"}, actual)


def test_json_type_names():
    assert [json_type(v) for v in (True, 1, 1.5, "s", [], {}, None)] == [
        "boolean", "number", "number", "string", "array", "object", "null"]
