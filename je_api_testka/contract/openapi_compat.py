"""
Bidirectional contract check: a consumer contract against the provider's OpenAPI document.

The provider publishes an OpenAPI document (kept honest by its own tests, e.g.
``apitestka openapi`` over its test run); the consumer publishes a contract.
This module checks that every interaction the consumer relies on is something
the provider's document allows, without running the provider:

* an operation exists for the method and path (path templates such as
  ``/items/{id}`` match, and the path of the first server URL is ignored);
* every query parameter the consumer sends is declared, and every required one is sent;
* a JSON request body satisfies the declared request body schema;
* the expected status code is declared (exactly, as ``2XX`` or as ``default``);
* the expected response body satisfies that response's JSON schema.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Tuple
from urllib.parse import parse_qsl

from je_api_testka.contract.openapi_schema import operation_parameters, resolve_ref, schema_errors
from je_api_testka.spec.path_templates import match_path_template, server_base_path, strip_base_path
from je_api_testka.utils.exception.exceptions import APIContractException

_JSON_MEDIA_SUFFIX: str = "json"


@dataclass
class CompatibilityReport:
    """Problems found per interaction; empty ``problems`` means the contract fits the document."""

    consumer: str
    provider: str
    checked: int = 0
    problems: List[Tuple[str, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when at least one interaction was checked and none had a problem."""
        return self.checked > 0 and not self.problems

    def to_dict(self) -> dict:
        """JSON-ready form: ``ok``, counts and ``{interaction, problem}`` pairs."""
        return {"ok": self.ok, "consumer": self.consumer, "provider": self.provider, "checked": self.checked,
                "problems": [{"interaction": name, "problem": problem} for name, problem in self.problems]}

    def render_text(self) -> str:
        """Plain-text summary with one line per problem."""
        lines = [f"Checking {self.consumer} contract against the {self.provider} OpenAPI document"]
        lines.extend(f"  [FAIL] {name}: {problem}" for name, problem in self.problems)
        failing = len({name for name, _problem in self.problems})
        lines.append(f"{self.checked - failing}/{self.checked} interactions compatible")
        return "\n".join(lines)


def _json_schema(content: Any) -> Optional[Mapping[str, Any]]:
    if not isinstance(content, Mapping):
        return None
    for media_type, media in content.items():
        if _JSON_MEDIA_SUFFIX in str(media_type) and isinstance(media, Mapping) and "schema" in media:
            return media["schema"]
    return None


def _declared_response(operation: Mapping[str, Any], status: int) -> Optional[Mapping[str, Any]]:
    responses = operation.get("responses") or {}
    for key in (str(status), f"{str(status)[0]}XX", f"{str(status)[0]}xx", "default"):
        if key in responses:
            return responses[key] or {}
    return None


def _query_problems(request: Mapping[str, Any], parameters: List[dict]) -> List[str]:
    sent = {name for name, _value in parse_qsl(str(request.get("query") or ""), keep_blank_values=True)}
    declared = {parameter["name"] for parameter in parameters if parameter.get("in") == "query"}
    required = {parameter["name"] for parameter in parameters
                if parameter.get("in") == "query" and parameter.get("required")}
    problems = [f"query parameter '{name}' is not declared" for name in sorted(sent - declared)]
    problems.extend(f"required query parameter '{name}' is not sent" for name in sorted(required - sent))
    return problems


def _body_problems(request: Mapping[str, Any], operation: Mapping[str, Any], spec: Mapping[str, Any]) -> List[str]:
    request_body = resolve_ref(operation.get("requestBody") or {}, spec)
    if "body" not in request:
        return ["request body is required but not sent"] if request_body.get("required") else []
    if not request_body:
        return ["request body is sent but the operation declares none"]
    schema = _json_schema(request_body.get("content"))
    if schema is None or not isinstance(request["body"], (dict, list)):
        return []
    return [f"request body {error}" for error in schema_errors(request["body"], schema, spec, "$.body")]


def _response_problems(response: Mapping[str, Any], operation: Mapping[str, Any],
                       spec: Mapping[str, Any]) -> List[str]:
    declared = _declared_response(operation, response["status"])
    if declared is None:
        return [f"status {response['status']} is not declared"]
    declared = resolve_ref(declared, spec)
    schema = _json_schema(declared.get("content"))
    if "body" not in response or schema is None:
        return []
    return [f"response body {error}" for error in schema_errors(response["body"], schema, spec, "$.body")]


def interaction_problems(interaction: Mapping[str, Any], spec: Mapping[str, Any]) -> List[str]:
    """Return why ``interaction`` is not allowed by ``spec`` (empty when it is)."""
    request = interaction["request"]
    path = strip_base_path(str(request["path"]), server_base_path(spec))
    paths = spec.get("paths") or {}
    template = match_path_template(path, paths)
    method = str(request["method"]).lower()
    if template is None or method not in (paths[template] or {}):
        return [f"no operation for {method.upper()} {path}"]
    path_item = paths[template]
    operation = path_item[method]
    problems = _query_problems(request, operation_parameters(path_item, operation, spec))
    problems.extend(_body_problems(request, operation, spec))
    problems.extend(_response_problems(interaction["response"], operation, spec))
    return problems


def check_pact_against_openapi(pact: Mapping[str, Any], spec: Mapping[str, Any]) -> CompatibilityReport:
    """Check every interaction of ``pact`` against the provider's OpenAPI document ``spec``."""
    report = CompatibilityReport(pact["consumer"]["name"], pact["provider"]["name"])
    for interaction in pact["interactions"]:
        report.checked += 1
        name = str(interaction["description"])
        report.problems.extend((name, problem) for problem in interaction_problems(interaction, spec))
    return report


def assert_pact_compatible(pact: Mapping[str, Any], spec: Mapping[str, Any]) -> dict:
    """
    Check ``pact`` against ``spec`` and return the report as a dict.

    :raises APIContractException: with the text report when any interaction does not fit.
    """
    report = check_pact_against_openapi(pact, spec)
    if not report.ok:
        raise APIContractException(report.render_text())
    return report.to_dict()
