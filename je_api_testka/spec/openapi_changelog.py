"""
Markdown changelog between two OpenAPI documents, layered on top of
``diff_openapi_specs``.
"""
from __future__ import annotations

from typing import Any, Mapping

from je_api_testka.diff.contract_diff import diff_openapi_specs


def _format_path_list(items: Any) -> list:
    return [f"- {item}" for item in sorted(items)]


def openapi_changelog(left: Mapping[str, Any], right: Mapping[str, Any]) -> str:
    """Return a markdown changelog describing how ``right`` deviates from ``left``."""
    diff = diff_openapi_specs(dict(left), dict(right))
    lines = ["# OpenAPI Changelog"]
    if diff.is_empty:
        lines.append("\nNo changes detected.")
        return "\n".join(lines)
    if diff.added_paths:
        lines.append("\n## Added paths")
        lines.extend(_format_path_list(diff.added_paths))
    if diff.removed_paths:
        lines.append("\n## Removed paths")
        lines.extend(_format_path_list(diff.removed_paths))
    if diff.added_operations:
        lines.append("\n## Added operations")
        lines.extend(_format_path_list(diff.added_operations))
    if diff.removed_operations:
        lines.append("\n## Removed operations")
        lines.extend(_format_path_list(diff.removed_operations))
    if diff.schema_changes:
        lines.append("\n## Schema changes")
        for operation, payload in sorted(diff.schema_changes.items()):
            lines.append(f"- {operation}")
            for key, value in payload.items():
                if value:
                    lines.append(f"  - {key}: {value}")
    return "\n".join(lines)
