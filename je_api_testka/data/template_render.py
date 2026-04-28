"""
``{{var}}`` template substitution against the global VariableStore.

Recursively walks dicts/lists and replaces double-curly tokens. Missing
variables default to an empty string but can be configured to raise.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from je_api_testka.data.variable_store import VariableStore, variable_store
from je_api_testka.utils.exception.exceptions import APITesterException

TEMPLATE_PATTERN = re.compile(r"\{\{\s*([\w\.\[\]]+)\s*\}\}")


def render_value(value: str, store: Optional[VariableStore] = None, strict: bool = False) -> str:
    """Substitute ``{{name}}`` placeholders inside a single string."""
    if not isinstance(value, str):
        return value
    active_store = store or variable_store

    def _replace(match: re.Match) -> str:
        name = match.group(1)
        result = active_store.get(name)
        if result is None:
            if strict:
                raise APITesterException(f"variable {name} is not defined")
            return ""
        return str(result)

    return TEMPLATE_PATTERN.sub(_replace, value)


def render_template(payload: Any, store: Optional[VariableStore] = None,
                    strict: bool = False) -> Any:
    """Recursively render ``{{var}}`` placeholders inside dicts/lists/strings."""
    if isinstance(payload, str):
        return render_value(payload, store=store, strict=strict)
    if isinstance(payload, dict):
        return {key: render_template(item, store=store, strict=strict)
                for key, item in payload.items()}
    if isinstance(payload, list):
        return [render_template(item, store=store, strict=strict) for item in payload]
    return payload
