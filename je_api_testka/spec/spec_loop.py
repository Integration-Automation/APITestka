"""
Test-as-spec loop: check a committed OpenAPI document against what the tests exercise.

One pass over the tests' records answers four questions:

* **drift**: does every recorded request fit the document? Each record is
  checked like a contract interaction (operation, query parameters, request
  body, status, response schema; see :mod:`je_api_testka.contract.openapi_compat`).
  A request to an operation the document does not declare is *undocumented*.
* **coverage**: which documented operations did no test exercise?
* **missing tests**: actions for the uncovered operations, through
  :func:`generate_tests_from_openapi` (the AI backend when one is set,
  otherwise deterministic requests built from the document's examples).
* **inferred spec**: the document the tests describe, with request paths
  grouped under the committed templates (``/items/7`` → ``/items/{id}``), for
  review or as the next version of the committed document.

The loop fails on undocumented operations, on any drift problem, and on
coverage below ``min_coverage``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import urlparse, urlunparse

from je_api_testka.ai.test_generator import generate_tests_from_openapi
from je_api_testka.contract.commands import read_openapi
from je_api_testka.contract.openapi_compat import interaction_problems
from je_api_testka.contract.pact import BODY_RULE_EQUALITY, interaction_from_record
from je_api_testka.spec.path_templates import (
    generalize_path,
    match_path_template,
    server_base_path,
    strip_base_path,
)
from je_api_testka.spec.openapi_export import collect_records
from je_api_testka.spec.records_to_openapi import records_to_openapi
from je_api_testka.utils.exception.exceptions import APIAssertException

HTTP_VERBS = ("get", "put", "post", "patch", "delete", "options", "head")
_NO_OPERATION: str = "no operation for "


@dataclass
class SpecLoopReport:
    """Coverage and drift of one test run against the committed document."""

    covered: List[str] = field(default_factory=list)
    uncovered: List[str] = field(default_factory=list)
    undocumented: List[str] = field(default_factory=list)
    problems: List[Tuple[str, str]] = field(default_factory=list)

    @property
    def coverage(self) -> float:
        """Share of documented operations the tests exercised (1.0 for a document without operations)."""
        total = len(self.covered) + len(self.uncovered)
        return len(self.covered) / total if total else 1.0

    def failures(self, min_coverage: float = 0.0) -> List[str]:
        """Return why the loop fails (empty when it passes)."""
        reasons = [f"undocumented operation {name}" for name in self.undocumented]
        reasons.extend(f"{name}: {problem}" for name, problem in self.problems)
        if self.coverage < min_coverage:
            reasons.append(f"coverage {self.coverage:.0%} is below {min_coverage:.0%}")
        return reasons

    def to_dict(self, min_coverage: float = 0.0) -> dict:
        """JSON-ready form, including ``ok`` and ``failures`` for ``min_coverage``."""
        failures = self.failures(min_coverage)
        return {"ok": not failures, "coverage": self.coverage, "covered": self.covered,
                "uncovered": self.uncovered, "undocumented": self.undocumented,
                "problems": [{"request": name, "problem": problem} for name, problem in self.problems],
                "failures": failures}

    def render_text(self, min_coverage: float = 0.0) -> str:
        """Plain-text summary: coverage, uncovered operations, then every failure."""
        lines = [f"Coverage: {len(self.covered)}/{len(self.covered) + len(self.uncovered)} operations "
                 f"({self.coverage:.0%})"]
        lines.extend(f"  [UNTESTED] {name}" for name in self.uncovered)
        lines.extend(f"  [FAIL] {reason}" for reason in self.failures(min_coverage))
        return "\n".join(lines)


def documented_operations(spec: Mapping[str, object]) -> List[str]:
    """Return ``"METHOD /template"`` for every operation in ``spec``."""
    return [f"{verb.upper()} {path}" for path, item in (spec.get("paths") or {}).items()
            for verb in HTTP_VERBS if isinstance(item, Mapping) and verb in item]


def _templated_path(url: str, spec: Mapping[str, object]) -> str:
    path = strip_base_path(urlparse(url).path or "/", server_base_path(spec))
    return match_path_template(path, spec.get("paths") or {}) or generalize_path(path)


def _append_once(items: list, item: object) -> None:
    if item not in items:
        items.append(item)


def _add_findings(report: SpecLoopReport, record: Mapping[str, object], spec: Mapping[str, object]) -> str:
    """Check one record, add its findings to ``report`` and return its ``"METHOD /template"``."""
    interaction = interaction_from_record(record, body_rule=BODY_RULE_EQUALITY)
    operation = f"{interaction['request']['method']} {_templated_path(str(record['request_url']), spec)}"
    for problem in interaction_problems(interaction, spec):
        if problem.startswith(_NO_OPERATION):
            _append_once(report.undocumented, operation)
        else:
            _append_once(report.problems, (interaction["description"], problem))
    return operation


def check_records_against_spec(records: Iterable[Mapping[str, object]], spec: Mapping[str, object]) -> SpecLoopReport:
    """Return coverage and drift of ``records`` (success records of a test run) against ``spec``."""
    documented = documented_operations(spec)
    report = SpecLoopReport()
    exercised = [_add_findings(report, record, spec) for record in records if record.get("request_url")]
    report.covered = [name for name in documented if name in exercised]
    report.uncovered = [name for name in documented if name not in exercised]
    return report


def uncovered_spec(spec: Mapping[str, object], uncovered: Iterable[str]) -> dict:
    """Return a copy of ``spec`` whose ``paths`` keep only the ``uncovered`` operations."""
    wanted = {tuple(name.split(" ", 1)) for name in uncovered}
    paths: dict = {}
    for path, item in (spec.get("paths") or {}).items():
        kept = {key: value for key, value in item.items()
                if key not in HTTP_VERBS or (key.upper(), path) in wanted}
        if any(key in HTTP_VERBS for key in kept):
            paths[path] = kept
    return {**spec, "paths": paths}


def missing_test_actions(spec: Mapping[str, object], report: SpecLoopReport) -> list:
    """Return executor actions for the operations no test exercised."""
    if not report.uncovered:
        return []
    return generate_tests_from_openapi(uncovered_spec(spec, report.uncovered))


def _with_templated_url(record: Mapping[str, object], spec: Mapping[str, object]) -> dict:
    parsed = urlparse(str(record["request_url"]))
    return {**record, "request_url": urlunparse(parsed._replace(path=_templated_path(parsed.geturl(), spec)))}


def _path_parameters(path: str) -> List[dict]:
    names = [segment[1:-1] for segment in path.split("/") if segment.startswith("{") and segment.endswith("}")]
    return [{"name": name, "in": "path", "required": True, "schema": {"type": "string"}} for name in names]


def infer_spec_from_tests(records: Iterable[Mapping[str, object]], spec: Mapping[str, object]) -> dict:
    """
    Return the OpenAPI document the ``records`` describe, paths grouped under ``spec``'s templates.

    ``info`` and ``servers`` are taken from ``spec``; templated paths get their path parameters.
    """
    templated = [_with_templated_url(record, spec) for record in records if record.get("request_url")]
    info = dict(spec.get("info") or {})
    inferred = records_to_openapi(templated, title=str(info.get("title", "APITestka Inferred")),
                                  version=str(info.get("version", "0.1.0")))
    for path, item in inferred["paths"].items():
        for operation in item.values():
            declared = {parameter["name"] for parameter in operation.get("parameters", [])}
            extra = [parameter for parameter in _path_parameters(path) if parameter["name"] not in declared]
            if extra:
                operation["parameters"] = [*extra, *operation.get("parameters", [])]
    if spec.get("servers"):
        inferred["servers"] = spec["servers"]
    return inferred


def check_spec_against_tests(spec_path: str, report_paths: Optional[Sequence[str]] = None,
                             min_coverage: float = 0.0, missing_actions_path: Optional[str] = None,
                             inferred_spec_path: Optional[str] = None) -> dict:
    """
    Run the loop for the OpenAPI JSON document at ``spec_path``.

    Records are the current test record plus saved JSON reports. Optionally writes the actions for
    uncovered operations (``missing_actions_path``) and the inferred document (``inferred_spec_path``).

    :raises APIAssertException: with the text report when the loop fails.
    """
    spec = read_openapi(spec_path)
    records = collect_records(report_paths)
    report = check_records_against_spec(records, spec)
    if missing_actions_path:
        write_json_document(missing_actions_path, missing_test_actions(spec, report))
    if inferred_spec_path:
        write_json_document(inferred_spec_path, infer_spec_from_tests(records, spec))
    if report.failures(min_coverage):
        raise APIAssertException(report.render_text(min_coverage))
    return report.to_dict(min_coverage)


def write_json_document(path: str, document: object) -> None:
    """Write ``document`` to ``path`` as indented UTF-8 JSON, creating parent folders."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
