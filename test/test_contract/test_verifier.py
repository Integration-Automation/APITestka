"""Tests for provider verification against a live provider."""
from __future__ import annotations

import pytest

from je_api_testka.contract.pact import add_interaction, new_pact
from je_api_testka.contract.verifier import ProviderTarget, assert_pact_verified, verify_pact
from je_api_testka.utils.exception.exceptions import APIContractException

TYPE = {"$.body": {"match": "type"}}


def _pact() -> dict:
    pact = new_pact("web", "shop")
    add_interaction(pact, "get item", {"method": "GET", "path": "/items/1"},
                    {"status": 200, "headers": {"Content-Type": "application/json"},
                     "body": {"id": 5, "name": "x", "tags": ["t"]}}, matching_rules=TYPE)
    add_interaction(pact, "create item", {"method": "POST", "path": "/items", "body": {"name": "n"}},
                    {"status": 201, "body": {"id": 99, "name": "n"}}, provider_state="catalogue is empty")
    add_interaction(pact, "ping", {"method": "GET", "path": "/ping"},
                    {"status": 200, "headers": {"Content-Type": "text/plain"}, "body": "pong"})
    return pact


def test_passing_contract_with_state_handler(provider):
    base_url, _states = provider
    seen = []
    report = verify_pact(_pact(), ProviderTarget(base_url, state_handler=seen.append, timeout=5))
    assert [result.mismatches for result in report.results] == [[], [], []]
    assert report.ok
    assert seen == ["catalogue is empty"]
    assert "3/3 interactions passed" in report.render_text()


def test_provider_states_url_gets_the_pact_convention_body(provider):
    base_url, states = provider
    verify_pact(_pact(), ProviderTarget(base_url, provider_states_url=f"{base_url}/_states", timeout=5))
    assert states == [{"consumer": "web", "state": "catalogue is empty"}]


def test_mismatches_are_reported(provider):
    base_url, _states = provider
    pact = new_pact("web", "shop")
    add_interaction(pact, "wrong status", {"method": "GET", "path": "/items/1"}, {"status": 201})
    add_interaction(pact, "wrong type", {"method": "GET", "path": "/items/1"},
                    {"status": 200, "body": {"id": "1"}}, matching_rules=TYPE)
    add_interaction(pact, "wrong header", {"method": "GET", "path": "/ping"},
                    {"status": 200, "headers": {"Content-Type": "application/json"}})
    report = verify_pact(pact, ProviderTarget(base_url, timeout=5))
    assert [result.mismatches for result in report.results] == [
        ["status: expected 201, got 200"],
        ["$.body.id: expected a string, got number 1"],
        ["$.headers.Content-Type: expected 'application/json', got 'text/plain; charset=utf-8'"],
    ]
    assert report.to_dict()["ok"] is False
    with pytest.raises(APIContractException):
        assert_pact_verified(pact, ProviderTarget(base_url, timeout=5))


def test_unreachable_provider_is_a_mismatch():
    pact = new_pact("web", "shop")
    add_interaction(pact, "get", {"method": "GET", "path": "/"}, {"status": 200})
    # Closed loopback port; nothing listens there.
    report = verify_pact(pact, ProviderTarget("http://127.0.0.1:9", timeout=2))  # NOSONAR S5332
    assert report.results[0].mismatches[0].startswith("request failed:")


def test_empty_contract_does_not_pass(provider):
    base_url, _states = provider
    assert not verify_pact(new_pact("web", "shop"), ProviderTarget(base_url)).ok
