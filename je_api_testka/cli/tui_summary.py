"""
Tiny terminal summary printer (no external TUI library).

Renders the current global test record as ANSI-coloured text suitable for
final-step CI output. For a richer experience install ``rich`` separately.
"""
from __future__ import annotations

from typing import TextIO

from je_api_testka.utils.test_record.test_record_class import test_record_instance

GREEN: str = "\033[32m"
RED: str = "\033[31m"
RESET: str = "\033[0m"
DIM: str = "\033[2m"


def render_terminal_summary() -> str:
    """Return a multi-line ANSI string summarising successes vs failures."""
    success = len(test_record_instance.test_record_list)
    failure = len(test_record_instance.error_record_list)
    lines = [
        f"{DIM}APITestka summary{RESET}",
        f"  {GREEN}OK    {success}{RESET}",
        f"  {RED}FAIL  {failure}{RESET}",
    ]
    if failure:
        lines.append(f"{RED}Recent failures:{RESET}")
        for entry in test_record_instance.error_record_list[-5:]:
            meta = entry[0] if entry and isinstance(entry[0], dict) else {}
            message = entry[1] if len(entry) > 1 else ""
            lines.append(f"  - {meta.get('test_url', '?')}: {message}")
    return "\n".join(lines)


def print_terminal_summary(stream: TextIO = None) -> None:
    import sys
    target = stream or sys.stdout
    print(render_terminal_summary(), file=target)
