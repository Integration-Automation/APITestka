"""
Check a JSON value against an OpenAPI 3.0 / 3.1 schema, without extra dependencies.

Covers what API descriptions commonly use: local ``$ref`` (``#/...``), ``type``
(a string or, in 3.1, a list), ``nullable`` (3.0), ``enum``, ``properties``,
``required``, ``additionalProperties: false``, ``items``, ``allOf``, ``anyOf``
and ``oneOf`` (treated like ``anyOf``). Unknown keywords are ignored, so the
check never rejects what a full validator would accept for those keywords.
"""
from __future__ import annotations

from typing import Any, List, Mapping

from je_api_testka.contract.matching import json_type

_MAX_REF_DEPTH: int = 32


def resolve_ref(schema: Mapping[str, Any], spec: Mapping[str, Any], depth: int = 0) -> Mapping[str, Any]:
    """Follow a local ``$ref`` (``#/components/...``) in ``spec``; other nodes come back unchanged."""
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/") or depth > _MAX_REF_DEPTH:
        return schema
    node: Any = spec
    for part in ref[2:].split("/"):
        node = node.get(part.replace("~1", "/").replace("~0", "~"), {}) if isinstance(node, Mapping) else {}
    return resolve_ref(node, spec, depth + 1) if isinstance(node, Mapping) else {}


def _type_matches(value: Any, schema: Mapping[str, Any]) -> bool:
    declared = schema.get("type")
    if declared is None:
        return True
    allowed = set(declared) if isinstance(declared, list) else {declared}
    if schema.get("nullable"):
        allowed.add("null")
    actual = json_type(value)
    if actual == "number" and isinstance(value, int):
        return bool(allowed & {"number", "integer"})
    return actual in allowed


def _object_errors(value: dict, schema: Mapping[str, Any], spec: Mapping[str, Any], path: str) -> List[str]:
    errors = [f"{path}.{name}: required" for name in schema.get("required", []) if name not in value]
    properties = schema.get("properties") or {}
    for name, item in value.items():
        if name in properties:
            errors.extend(schema_errors(item, properties[name], spec, f"{path}.{name}"))
        elif schema.get("additionalProperties") is False:
            errors.append(f"{path}.{name}: not allowed")
    return errors


def _combinator_errors(value: Any, schema: Mapping[str, Any], spec: Mapping[str, Any], path: str) -> List[str]:
    errors: List[str] = []
    for part in schema.get("allOf", []):
        errors.extend(schema_errors(value, part, spec, path))
    for keyword in ("anyOf", "oneOf"):
        options = schema.get(keyword)
        if options and all(schema_errors(value, option, spec, path) for option in options):
            errors.append(f"{path}: matches none of {keyword}")
    return errors


def schema_errors(value: Any, schema: Mapping[str, Any], spec: Mapping[str, Any], path: str = "$") -> List[str]:
    """Return why ``value`` does not satisfy ``schema`` (empty when it does); ``spec`` resolves ``$ref``."""
    schema = resolve_ref(schema, spec)
    if value is None and schema.get("nullable"):
        return []
    if not _type_matches(value, schema):
        return [f"{path}: expected type {schema.get('type')}, got {json_type(value)}"]
    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: {value!r} is not one of {schema['enum']}"]
    errors = _combinator_errors(value, schema, spec, path)
    if isinstance(value, dict):
        errors.extend(_object_errors(value, schema, spec, path))
    elif isinstance(value, list) and isinstance(schema.get("items"), Mapping):
        for index, item in enumerate(value):
            errors.extend(schema_errors(item, schema["items"], spec, f"{path}[{index}]"))
    return errors
