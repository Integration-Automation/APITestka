"""
File-level contract steps used by the executor (``AT_*``) and ``apitestka contract``.

* consumer side: :func:`write_contract` records a contract from test records;
* provider side: :func:`verify_contract` replays it against a running provider;
* bidirectional: :func:`check_contract_against_openapi` compares it with the
  provider's OpenAPI document without running the provider.

The checking steps return a JSON-ready report and raise
:class:`APIContractException` (carrying the text report) when the contract does
not hold, so a failing step shows up as a failed action.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Sequence

from je_api_testka.contract.openapi_compat import assert_pact_compatible
from je_api_testka.contract.pact import BODY_RULE_TYPE, pact_from_records, read_pact, write_pact
from je_api_testka.contract.verifier import DEFAULT_VERIFY_TIMEOUT_SECONDS, ProviderTarget, assert_pact_verified
from je_api_testka.spec.openapi_export import collect_records
from je_api_testka.utils.exception.exceptions import APIContractException


def write_contract(output_path: str, consumer: str, provider: str, report_paths: Optional[Sequence[str]] = None,
                   base_path: str = "", body_rule: str = BODY_RULE_TYPE) -> str:
    """
    Record a consumer contract from the current test record plus saved JSON reports and write it.

    :raises APIContractException: when there is no record to build an interaction from.
    """
    pact = pact_from_records(collect_records(report_paths), consumer, provider,
                             base_path=base_path, body_rule=body_rule)
    if not pact["interactions"]:
        raise APIContractException("no successful records to build a contract from")
    return write_pact(pact, output_path)


def verify_contract(contract_path: str, base_url: str, provider_states_url: Optional[str] = None,
                    timeout: float = DEFAULT_VERIFY_TIMEOUT_SECONDS) -> dict:
    """Replay the contract at ``contract_path`` against the provider at ``base_url``."""
    target = ProviderTarget(base_url, provider_states_url=provider_states_url, timeout=timeout)
    return assert_pact_verified(read_pact(contract_path), target)


def read_openapi(openapi_path: str) -> dict:
    """
    Read an OpenAPI JSON document.

    :raises APIContractException: when the file is missing, not JSON or not a JSON object.
    """
    try:
        spec = json.loads(Path(openapi_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise APIContractException(f"{openapi_path}: cannot read OpenAPI document: {error!r}") from error
    if not isinstance(spec, dict):
        raise APIContractException(f"{openapi_path}: an OpenAPI document is a JSON object")
    return spec


def check_contract_against_openapi(contract_path: str, openapi_path: str) -> dict:
    """Check the contract at ``contract_path`` against the OpenAPI JSON document at ``openapi_path``."""
    return assert_pact_compatible(read_pact(contract_path), read_openapi(openapi_path))
