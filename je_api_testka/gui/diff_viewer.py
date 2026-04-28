"""
Side-by-side diff renderer.

Layered on top of :func:`diff_payloads`; emits a multi-line string suitable
for a Qt monospaced text viewer or a CLI dump.
"""
from __future__ import annotations

from typing import Any

from je_api_testka.diff.response_diff import diff_payloads


def render_side_by_side(left: Any, right: Any, width: int = 40) -> str:
    """Return a two-column diff, with ``+`` / ``-`` / ``~`` markers per row."""
    diff = diff_payloads(left, right)
    rows = [_format_row("path", "left", "right", width)]
    rows.append("-" * (width * 3 + 8))
    for key, value in sorted(diff.removed.items()):
        rows.append(_format_row(f"- {key}", repr(value), "", width))
    for key, value in sorted(diff.added.items()):
        rows.append(_format_row(f"+ {key}", "", repr(value), width))
    for key, (left_value, right_value) in sorted(diff.changed.items()):
        rows.append(_format_row(f"~ {key}", repr(left_value), repr(right_value), width))
    if diff.is_empty:
        rows.append("(identical)")
    return "\n".join(rows)


def _format_row(path: str, left: str, right: str, width: int) -> str:
    return f"{path[:width].ljust(width)} | {left[:width].ljust(width)} | {right[:width]}"
