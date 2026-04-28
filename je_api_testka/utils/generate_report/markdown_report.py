"""
Markdown report renderer.

Suitable for pasting into GitHub issues, PR descriptions, or Slack threads.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_MARKDOWN_FILENAME: str = "apitestka_report.md"


def _format_success_row(record: dict) -> str:
    return (
        f"| {record.get('request_method', '?')} "
        f"| {record.get('request_url', '?')} "
        f"| {record.get('status_code', '?')} "
        f"| {record.get('request_time_sec', '?')} |"
    )


def _format_failure_row(record: list) -> str:
    meta = record[0] if record and isinstance(record[0], dict) else {}
    message = record[1] if len(record) > 1 else ""
    return (
        f"| {meta.get('http_method', '?')} "
        f"| {meta.get('test_url', '?')} "
        f"| {message} |"
    )


def render_markdown(title: str = "APITestka Report") -> str:
    """Render the global test record into a markdown string."""
    lines: List[str] = [f"# {title}", ""]
    successes = list(test_record_instance.test_record_list)
    failures = list(test_record_instance.error_record_list)

    lines.append(f"**Successes:** {len(successes)}  ")
    lines.append(f"**Failures:** {len(failures)}")
    lines.append("")

    if successes:
        lines.append("## Successful requests")
        lines.append("| Method | URL | Status | Elapsed (s) |")
        lines.append("|---|---|---|---|")
        lines.extend(_format_success_row(record) for record in successes)
        lines.append("")
    if failures:
        lines.append("## Failed requests")
        lines.append("| Method | URL | Error |")
        lines.append("|---|---|---|")
        lines.extend(_format_failure_row(record) for record in failures)
        lines.append("")
    return "\n".join(lines)


def generate_markdown_report(file_name: str = DEFAULT_MARKDOWN_FILENAME,
                             title: Optional[str] = None) -> Path:
    """Write the markdown report to disk and return the path."""
    target = Path(file_name)
    target.write_text(render_markdown(title or "APITestka Report"), encoding="utf-8")
    return target
