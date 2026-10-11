"""
Deterministic example values from an OpenAPI document.

Used to turn an operation into a runnable request: path parameters, required
query parameters and a JSON request body come from the document's ``example``
/ ``examples`` / ``default`` / ``enum`` values when present, otherwise from the
schema type. Values are fixed (no random data), so generated tests are
reproducible. Local ``$ref`` is followed; recursion stops at a fixed depth.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Mapping, Optional
from urllib.parse import quote

from je_api_testka.contract.openapi_schema import resolve_ref

_MAX_DEPTH: int = 8
_PARAMETER = re.compile(r"\{([^/{}]+)\}")
_STRING_FORMATS: Dict[str, str] = {
    "uuid": "00000000-0000-4000-8000-000000000000",
    "email": "user@example.com",
    "date": "2026-01-01",
    "date-time": "2026-01-01T00:00:00Z",
    "uri": "https://example.com/",
}
_TYPE_EXAMPLES: Dict[str, Any] = {"integer": 1, "number": 1.0, "boolean": True, "null": None, "string": "string"}


def _declared_example(node: Mapping[str, Any]) -> tuple:
    if "example" in node:
        return True, node["example"]
    examples = node.get("examples")
    if isinstance(examples, Mapping) and examples:
        first = next(iter(examples.values()))
        return True, first.get("value") if isinstance(first, Mapping) else first
    if isinstance(examples, list) and examples:
        return True, examples[0]
    return False, None


def example_value(schema: Mapping[str, Any], spec: Mapping[str, Any], depth: int = 0) -> Any:
    """Return an example that fits ``schema`` (``$ref`` resolved against ``spec``)."""
    schema = resolve_ref(schema, spec)
    found, value = _declared_example(schema)
    if found:
        return value
    if "default" in schema:
        return schema["default"]
    if schema.get("enum"):
        return schema["enum"][0]
    for keyword in ("allOf", "anyOf", "oneOf"):
        if schema.get(keyword) and depth < _MAX_DEPTH:
            return _combined(schema, keyword, spec, depth)
    return _typed_example(schema, spec, depth)


def _schema_type(schema: Mapping[str, Any]) -> Optional[str]:
    declared = schema.get("type")
    if isinstance(declared, list):  # OpenAPI 3.1 type lists: prefer the first non-null type
        return next((kind for kind in declared if kind != "null"), "null")
    if declared is None and "properties" in schema:
        return "object"
    return declared


def _typed_example(schema: Mapping[str, Any], spec: Mapping[str, Any], depth: int) -> Any:
    schema_type = _schema_type(schema)
    if schema_type == "object":
        if depth >= _MAX_DEPTH:
            return {}
        return {name: example_value(part, spec, depth + 1) for name, part in (schema.get("properties") or {}).items()}
    if schema_type == "array":
        return [] if depth >= _MAX_DEPTH else [example_value(schema.get("items") or {}, spec, depth + 1)]
    if schema_type == "string":
        return _STRING_FORMATS.get(str(schema.get("format", "")), "string")
    return _TYPE_EXAMPLES.get(schema_type, "string")


def _combined(schema: Mapping[str, Any], keyword: str, spec: Mapping[str, Any], depth: int) -> Any:
    if keyword != "allOf":
        return example_value(schema[keyword][0], spec, depth + 1)
    merged: Dict[str, Any] = {}
    for part in schema["allOf"]:
        value = example_value(part, spec, depth + 1)
        if not isinstance(value, dict):
            return value
        merged.update(value)
    return merged


def parameter_example(parameter: Mapping[str, Any], spec: Mapping[str, Any]) -> Any:
    """Return an example for one parameter object."""
    parameter = resolve_ref(parameter, spec)
    found, value = _declared_example(parameter)
    return value if found else example_value(parameter.get("schema") or {}, spec)


def fill_path(template: str, values: Mapping[str, Any]) -> str:
    """Replace each ``{name}`` in ``template`` with its URL-quoted value (``1`` when there is none)."""
    return _PARAMETER.sub(lambda match: quote(str(values.get(match.group(1), 1)), safe=""), template)


def success_status(operation: Mapping[str, Any]) -> int:
    """Return the lowest declared 2xx status of ``operation`` (200 when none is declared exactly)."""
    codes = sorted(int(code) for code in (operation.get("responses") or {}) if str(code).isdigit()
                   and str(code).startswith("2"))
    return codes[0] if codes else 200


def request_body_example(operation: Mapping[str, Any], spec: Mapping[str, Any]) -> Optional[Any]:
    """Return an example JSON request body, or ``None`` when the operation declares no JSON body."""
    request_body = resolve_ref(operation.get("requestBody") or {}, spec)
    for media_type, media in (request_body.get("content") or {}).items():
        if "json" not in str(media_type) or not isinstance(media, Mapping):
            continue
        found, value = _declared_example(media)
        return value if found else example_value(media.get("schema") or {}, spec)
    return None
