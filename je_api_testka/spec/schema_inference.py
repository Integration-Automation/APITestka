"""
Infer a JSON Schema fragment from a sample payload.

Recurses into objects and arrays; the inferred schema is the simplest one
that the sample satisfies. For arrays, schema of the first non-null element
is used; mixed-type arrays are reduced to ``{}``.
"""
from __future__ import annotations

from typing import Any


def _scalar_schema(value: Any) -> dict:
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, str):
        return {"type": "string"}
    if value is None:
        return {"type": "null"}
    return {}


def infer_schema(sample: Any) -> dict:
    """Return a minimal JSON Schema describing ``sample``."""
    if isinstance(sample, dict):
        properties = {key: infer_schema(value) for key, value in sample.items()}
        return {"type": "object", "properties": properties, "required": sorted(sample.keys())}
    if isinstance(sample, list):
        if not sample:
            return {"type": "array", "items": {}}
        first = sample[0]
        return {"type": "array", "items": infer_schema(first)}
    return _scalar_schema(sample)
