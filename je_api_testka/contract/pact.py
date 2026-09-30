"""
Consumer contracts in the Pact specification v2 file format.

A contract lists the interactions a consumer relies on: the request it sends
and the response it expects, plus ``matchingRules`` that loosen exact equality
(``type`` or ``regex``). Files written here can go to a Pact Broker or Pactflow
as they are.

Contracts are usually recorded from the consumer's own test run
(:func:`pact_from_records`). By default the response body gets a ``type`` rule
on ``$.body``, so the provider must return the same structure and value types,
not the same values.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, Optional
from urllib.parse import urlparse

from je_api_testka.spec.path_templates import strip_base_path
from je_api_testka.spec.records_to_openapi import decode_body
from je_api_testka.utils.exception.exceptions import APIContractException

PACT_SPECIFICATION_VERSION: str = "2.0.0"
BODY_RULE_TYPE: str = "type"
BODY_RULE_EQUALITY: str = "equality"
_BODY_RULES = (BODY_RULE_TYPE, BODY_RULE_EQUALITY)
_CONTENT_TYPE: str = "Content-Type"


def new_pact(consumer: str, provider: str) -> dict:
    """Return an empty Pact v2 document for ``consumer`` and ``provider``."""
    return {
        "consumer": {"name": consumer},
        "provider": {"name": provider},
        "interactions": [],
        "metadata": {"pactSpecification": {"version": PACT_SPECIFICATION_VERSION}},
    }


def add_interaction(pact: dict, description: str, request: Mapping[str, object], response: Mapping[str, object],
                    provider_state: Optional[str] = None,
                    matching_rules: Optional[Mapping[str, Mapping[str, object]]] = None) -> dict:
    """
    Append one interaction to ``pact`` and return it.

    ``request`` needs ``method`` and ``path`` (``query`` as a query string, ``headers``, ``body`` optional);
    ``response`` needs ``status`` (``headers``, ``body`` optional). ``matching_rules`` are
    Pact v2 rules such as ``{"$.body.id": {"match": "type"}}``.

    :raises APIContractException: on a missing field or a description already in the contract.
    """
    if not request.get("method") or not str(request.get("path", "")).startswith("/"):
        raise APIContractException("an interaction request needs a method and a path starting with '/'")
    if not isinstance(response.get("status"), int):
        raise APIContractException("an interaction response needs an integer status")
    if any(existing["description"] == description for existing in pact["interactions"]):
        raise APIContractException(f"duplicate interaction description: {description!r}")
    interaction: dict = {"description": description}
    if provider_state:
        interaction["providerState"] = provider_state
    interaction["request"] = {**request, "method": str(request["method"]).upper()}
    interaction["response"] = dict(response)
    if matching_rules:
        interaction["response"]["matchingRules"] = dict(matching_rules)
    pact["interactions"].append(interaction)
    return interaction


def _content_type(headers: object) -> Optional[str]:
    if not isinstance(headers, Mapping):
        return None
    for name, value in headers.items():
        if str(name).lower() == _CONTENT_TYPE.lower():
            return str(value)
    return None


def _request_part(record: Mapping[str, object], base_path: str) -> dict:
    parsed = urlparse(str(record["request_url"]))
    request: dict = {"method": str(record.get("request_method") or "GET").upper(),
                     "path": strip_base_path(parsed.path or "/", base_path)}
    if parsed.query:
        request["query"] = parsed.query
    body = decode_body(record.get("request_body"))
    if body is not None:
        request["body"] = body[1]
    return request


def _response_part(record: Mapping[str, object]) -> dict:
    response: dict = {"status": int(str(record.get("status_code", 200)))}
    content_type = _content_type(record.get("headers"))
    body = decode_body(record.get("text"))
    if content_type:
        response["headers"] = {_CONTENT_TYPE: content_type}
    if body is not None:
        response["body"] = body[1]
    return response


def interaction_from_record(record: Mapping[str, object], base_path: str = "",
                            body_rule: str = BODY_RULE_TYPE) -> dict:
    """
    Turn one success record into an interaction (not yet added to a contract).

    ``base_path`` is removed from the request path, e.g. ``/api/v1`` when the provider is
    verified at ``https://host/api/v1``. ``body_rule`` is ``"type"`` (the default) or ``"equality"``.
    """
    if body_rule not in _BODY_RULES:
        raise APIContractException(f"body_rule must be one of {_BODY_RULES}, not {body_rule!r}")
    request = _request_part(record, base_path)
    response = _response_part(record)
    query = f"?{request['query']}" if "query" in request else ""
    interaction = {
        "description": f"{request['method']} {request['path']}{query} -> {response['status']}",
        "request": request,
        "response": response,
    }
    if body_rule == BODY_RULE_TYPE and "body" in response:
        response["matchingRules"] = {"$.body": {"match": "type"}}
    return interaction


def pact_from_records(records: Iterable[Mapping[str, object]], consumer: str, provider: str,
                      base_path: str = "", body_rule: str = BODY_RULE_TYPE) -> dict:
    """
    Build a contract from success records; records without a ``request_url`` are skipped.

    Records that yield the same description (method, path, query and status) are kept once.
    """
    pact = new_pact(consumer, provider)
    for record in records:
        if not record.get("request_url"):
            continue
        interaction = interaction_from_record(record, base_path=base_path, body_rule=body_rule)
        if all(existing["description"] != interaction["description"] for existing in pact["interactions"]):
            pact["interactions"].append(interaction)
    return pact


def write_pact(pact: Mapping[str, object], path: str) -> str:
    """Write ``pact`` to ``path`` as UTF-8 JSON (creating parent folders) and return the path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(pact, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(target)


def _check_interaction(interaction: object, index: int) -> None:
    if not isinstance(interaction, dict) or not isinstance(interaction.get("description"), str):
        raise APIContractException(f"interaction {index} needs a description")
    request = interaction.get("request")
    response = interaction.get("response")
    if not isinstance(request, dict) or not request.get("method") or not isinstance(request.get("path"), str):
        raise APIContractException(f"interaction {index} needs request.method and request.path")
    if not isinstance(response, dict) or not isinstance(response.get("status"), int):
        raise APIContractException(f"interaction {index} needs an integer response.status")


def read_pact(path: str) -> dict:
    """
    Read and validate a contract file.

    :raises APIContractException: when the file is not JSON or misses consumer, provider or interaction fields.
    """
    try:
        pact = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise APIContractException(f"{path}: cannot read contract: {error!r}") from error
    if not isinstance(pact, dict) or not isinstance(pact.get("interactions"), list):
        raise APIContractException(f"{path}: a contract is an object with an interactions list")
    for party in ("consumer", "provider"):
        if not isinstance(pact.get(party), dict) or not pact[party].get("name"):
            raise APIContractException(f"{path}: missing {party}.name")
    for index, interaction in enumerate(pact["interactions"]):
        _check_interaction(interaction, index)
    return pact
