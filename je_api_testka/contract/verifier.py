"""
Provider verification: replay a consumer contract against a running provider.

Each interaction's request is sent to ``base_url`` and the response is checked
with :mod:`je_api_testka.contract.matching`: the status must be equal, the
contract's headers must be present, and the body must satisfy the matching
rules. When an interaction names a ``providerState``, the provider is first put
into that state through a Python callable or a setup URL, which receives
``{"consumer": ..., "state": ...}`` as a JSON POST (the Pact convention).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, List, Mapping, Optional

import requests

from je_api_testka.contract.matching import body_mismatches, header_mismatches
from je_api_testka.utils.exception.exceptions import APIContractException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_VERIFY_TIMEOUT_SECONDS: float = 10.0

StateHandler = Callable[[str], None]


@dataclass
class InteractionResult:
    """Outcome of one interaction."""

    description: str
    mismatches: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when the provider satisfied the interaction."""
        return not self.mismatches


@dataclass
class VerificationReport:
    """Outcome of verifying one contract against one provider."""

    consumer: str
    provider: str
    results: List[InteractionResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when every interaction passed (and there was at least one)."""
        return bool(self.results) and all(result.ok for result in self.results)

    def to_dict(self) -> dict:
        """JSON-ready form: ``ok``, the parties, and each interaction's mismatches."""
        return {
            "ok": self.ok,
            "consumer": self.consumer,
            "provider": self.provider,
            "interactions": [{"description": result.description, "ok": result.ok, "mismatches": result.mismatches}
                             for result in self.results],
        }

    def render_text(self) -> str:
        """Plain-text summary, one line per interaction and one indented line per mismatch."""
        lines = [f"Verifying {self.consumer} -> {self.provider}"]
        for result in self.results:
            lines.append(f"  [{'PASS' if result.ok else 'FAIL'}] {result.description}")
            lines.extend(f"      {mismatch}" for mismatch in result.mismatches)
        passed = sum(result.ok for result in self.results)
        lines.append(f"{passed}/{len(self.results)} interactions passed")
        return "\n".join(lines)


@dataclass
class ProviderTarget:
    """Where and how to reach the provider under verification."""

    base_url: str
    state_handler: Optional[StateHandler] = None
    provider_states_url: Optional[str] = None
    timeout: float = DEFAULT_VERIFY_TIMEOUT_SECONDS


def _set_up_state(target: ProviderTarget, consumer: str, state: str) -> None:
    if target.state_handler is not None:
        target.state_handler(state)
    if target.provider_states_url:
        response = requests.post(target.provider_states_url, json={"consumer": consumer, "state": state},
                                 timeout=target.timeout)
        response.raise_for_status()


def _send(target: ProviderTarget, request: Mapping[str, object]) -> requests.Response:
    url = target.base_url.rstrip("/") + str(request["path"])
    if request.get("query"):
        url += f"?{request['query']}"
    body = request.get("body")
    return requests.request(
        str(request["method"]), url, headers=dict(request.get("headers") or {}),
        json=body if isinstance(body, (dict, list)) else None,
        data=None if body is None or isinstance(body, (dict, list)) else str(body),
        timeout=target.timeout, allow_redirects=False,
    )


def _actual_body(response: requests.Response, expected: object) -> object:
    if isinstance(expected, str):
        return response.text
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError):
        return response.text


def _check_response(expected: Mapping[str, object], response: requests.Response) -> List[str]:
    rules = expected.get("matchingRules") or {}
    mismatches: List[str] = []
    if response.status_code != expected["status"]:
        mismatches.append(f"status: expected {expected['status']}, got {response.status_code}")
    mismatches.extend(header_mismatches(expected.get("headers") or {}, response.headers, rules))
    if "body" in expected:
        mismatches.extend(body_mismatches(expected["body"], _actual_body(response, expected["body"]), rules))
    return mismatches


def verify_interaction(interaction: Mapping[str, object], target: ProviderTarget,
                       consumer: str = "") -> InteractionResult:
    """Replay one interaction against ``target`` and return its result."""
    result = InteractionResult(str(interaction["description"]))
    try:
        if interaction.get("providerState"):
            _set_up_state(target, consumer, str(interaction["providerState"]))
        response = _send(target, interaction["request"])
    except requests.RequestException as error:
        result.mismatches.append(f"request failed: {error!r}")
        return result
    result.mismatches.extend(_check_response(interaction["response"], response))
    return result


def verify_pact(pact: Mapping[str, object], target: ProviderTarget) -> VerificationReport:
    """Replay every interaction of ``pact`` against ``target``; the report says which ones failed and why."""
    consumer = pact["consumer"]["name"]
    report = VerificationReport(consumer, pact["provider"]["name"])
    for interaction in pact["interactions"]:
        result = verify_interaction(interaction, target, consumer)
        apitestka_logger.info(f"contract verify {result.description}: {'ok' if result.ok else result.mismatches}")
        report.results.append(result)
    return report


def assert_pact_verified(pact: Mapping[str, object], target: ProviderTarget) -> dict:
    """
    Verify ``pact`` and return the report as a dict.

    :raises APIContractException: with the text report when any interaction fails.
    """
    report = verify_pact(pact, target)
    if not report.ok:
        raise APIContractException(report.render_text())
    return report.to_dict()
