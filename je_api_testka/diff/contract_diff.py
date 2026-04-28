"""
OpenAPI contract drift detection.

Compares two OpenAPI 3.x dicts and reports:
* ``added_paths`` / ``removed_paths``
* ``added_operations`` / ``removed_operations``
* ``schema_changes`` for shared operations whose response schema diverged.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from je_api_testka.diff.response_diff import diff_payloads

HTTP_VERBS: Tuple[str, ...] = ("get", "put", "post", "patch", "delete", "options", "head")


@dataclass
class ContractDiff:
    """Aggregated drift between two OpenAPI specifications."""

    added_paths: Set[str] = field(default_factory=set)
    removed_paths: Set[str] = field(default_factory=set)
    added_operations: List[str] = field(default_factory=list)
    removed_operations: List[str] = field(default_factory=list)
    schema_changes: Dict[str, dict] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not (
            self.added_paths or self.removed_paths
            or self.added_operations or self.removed_operations
            or self.schema_changes
        )


def _operation_keys(spec: dict) -> Set[str]:
    keys: Set[str] = set()
    for path, item in (spec.get("paths") or {}).items():
        for verb in HTTP_VERBS:
            if (item or {}).get(verb):
                keys.add(f"{verb.upper()} {path}")
    return keys


def _operation_response_schema(spec: dict, key: str) -> dict:
    verb, path = key.split(" ", 1)
    operation = ((spec.get("paths") or {}).get(path) or {}).get(verb.lower()) or {}
    responses = operation.get("responses") or {}
    return responses


def diff_openapi_specs(left: dict, right: dict) -> ContractDiff:
    """Return a :class:`ContractDiff` describing how ``right`` deviates from ``left``."""
    diff = ContractDiff()
    left_paths = set((left.get("paths") or {}).keys())
    right_paths = set((right.get("paths") or {}).keys())
    diff.added_paths = right_paths - left_paths
    diff.removed_paths = left_paths - right_paths

    left_ops = _operation_keys(left)
    right_ops = _operation_keys(right)
    diff.added_operations = sorted(right_ops - left_ops)
    diff.removed_operations = sorted(left_ops - right_ops)

    for shared in left_ops & right_ops:
        payload_left = _operation_response_schema(left, shared)
        payload_right = _operation_response_schema(right, shared)
        payload_diff = diff_payloads(payload_left, payload_right)
        if not payload_diff.is_empty:
            diff.schema_changes[shared] = {
                "added": payload_diff.added,
                "removed": payload_diff.removed,
                "changed": payload_diff.changed,
            }
    return diff
