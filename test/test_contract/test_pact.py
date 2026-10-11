"""Tests for Pact v2 contract files."""
from __future__ import annotations

import json

import pytest

from je_api_testka.contract.pact import (
    add_interaction,
    interaction_from_record,
    new_pact,
    pact_from_records,
    read_pact,
    write_pact,
)
from je_api_testka.utils.exception.exceptions import APIContractException


def _record(url="https://api.invalid/api/v1/items/1?full=1", method="GET", status=200,
            text='{"id": 1}', body=None, headers=None):
    return {"request_url": url, "request_method": method, "status_code": status, "text": text,
            "request_body": body, "headers": headers or {"content-type": "application/json"}}


def test_new_pact_is_pact_v2():
    pact = new_pact("web", "shop")
    assert pact["consumer"] == {"name": "web"}
    assert pact["provider"] == {"name": "shop"}
    assert pact["metadata"]["pactSpecification"]["version"] == "2.0.0"


def test_interaction_from_record_with_type_rule():
    interaction = interaction_from_record(_record(), base_path="/api/v1")
    assert interaction["description"] == "GET /items/1?full=1 -> 200"
    assert interaction["request"] == {"method": "GET", "path": "/items/1", "query": "full=1"}
    assert interaction["response"] == {
        "status": 200, "headers": {"Content-Type": "application/json"}, "body": {"id": 1},
        "matchingRules": {"$.body": {"match": "type"}},
    }


def test_equality_rule_and_request_body():
    interaction = interaction_from_record(
        _record(url="https://api.invalid/items", method="post", status=201, body=b'{"name": "a"}'),
        body_rule="equality")
    assert interaction["request"]["body"] == {"name": "a"}
    assert "matchingRules" not in interaction["response"]


def test_unknown_body_rule_raises():
    with pytest.raises(APIContractException):
        interaction_from_record(_record(), body_rule="loose")


def test_pact_from_records_skips_and_deduplicates():
    pact = pact_from_records([_record(), _record(), {"status_code": 200}, _record(status=404)], "web", "shop")
    assert [i["description"] for i in pact["interactions"]] == [
        "GET /api/v1/items/1?full=1 -> 200", "GET /api/v1/items/1?full=1 -> 404"]


def test_add_interaction_validates():
    pact = new_pact("web", "shop")
    add_interaction(pact, "get item", {"method": "get", "path": "/items/1"}, {"status": 200},
                    provider_state="item 1 exists", matching_rules={"$.body.id": {"match": "type"}})
    interaction = pact["interactions"][0]
    assert interaction["providerState"] == "item 1 exists"
    assert interaction["request"]["method"] == "GET"
    assert interaction["response"]["matchingRules"] == {"$.body.id": {"match": "type"}}
    with pytest.raises(APIContractException):
        add_interaction(pact, "get item", {"method": "GET", "path": "/x"}, {"status": 200})
    with pytest.raises(APIContractException):
        add_interaction(pact, "no path", {"method": "GET", "path": "x"}, {"status": 200})
    with pytest.raises(APIContractException):
        add_interaction(pact, "bad status", {"method": "GET", "path": "/x"}, {"status": "200"})


def test_write_and_read_round_trip(tmp_path):
    pact = pact_from_records([_record()], "web", "shop")
    path = write_pact(pact, str(tmp_path / "pacts" / "web-shop.json"))
    assert read_pact(path) == pact


@pytest.mark.parametrize("document", [
    [], {"interactions": []}, {"consumer": {"name": "a"}, "provider": {}, "interactions": []},
    {"consumer": {"name": "a"}, "provider": {"name": "b"}, "interactions": [{"description": "x"}]},
    {"consumer": {"name": "a"}, "provider": {"name": "b"}, "interactions": [
        {"description": "x", "request": {"method": "GET", "path": "/"}, "response": {"status": "200"}}]},
])
def test_read_pact_rejects_malformed(tmp_path, document):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(APIContractException):
        read_pact(str(path))


def test_read_pact_rejects_unreadable(tmp_path):
    with pytest.raises(APIContractException):
        read_pact(str(tmp_path / "missing.json"))
