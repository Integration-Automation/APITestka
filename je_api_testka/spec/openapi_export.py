"""
Build and write an inferred OpenAPI document from recorded traffic.

Records come from the in-memory test record and from saved JSON reports, so a
fresh process (the ``apitestka openapi`` CLI, the MCP server) can still infer a
spec from an earlier run.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, List, Optional, Sequence

from je_api_testka.spec.records_to_openapi import DEFAULT_SPEC_TITLE, DEFAULT_SPEC_VERSION, records_to_openapi
from je_api_testka.utils.exception.exceptions import APIJsonReportException
from je_api_testka.utils.test_record.test_record_class import test_record_instance

# generate_json_report writes every field through str(): None becomes "None"
# and a bytes request body becomes its repr, b'...'.
_REPORT_NONE: str = "None"
_BYTES_REPR = re.compile(r"^b(['\"]).*\1$", re.DOTALL)


def _report_value(value: Any) -> Any:
    if value == _REPORT_NONE:
        return None
    if isinstance(value, str) and _BYTES_REPR.match(value):
        # literal_eval only builds literals; the regex restricts it to one bytes literal.
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
    return value


def _record_entries(document: Any, path: str) -> List[Any]:
    if isinstance(document, list):
        return document
    if isinstance(document, dict) and isinstance(document.get("successes"), list):
        return document["successes"]
    if isinstance(document, dict):
        return list(document.values())
    raise APIJsonReportException(f"{path}: expected a JSON report object or a list of records")


def load_report_records(path: str) -> List[dict]:
    """
    Read success records back from a saved report.

    Accepts the ``<name>_success.json`` file written by ``generate_json_report``,
    the ``{"successes": [...]}`` object returned by the ``apitestka_get_records``
    MCP tool, or a plain list of record objects.

    :raises APIJsonReportException: if the file is not JSON or an entry is not a record object.
    """
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise APIJsonReportException(f"{path}: cannot read report: {error!r}") from error
    records = []
    for entry in _record_entries(document, path):
        if not isinstance(entry, dict) or "request_url" not in entry:
            raise APIJsonReportException(f"{path}: every record needs a request_url")
        records.append({key: _report_value(value) for key, value in entry.items()})
    return records


def collect_records(report_paths: Optional[Sequence[str]] = None) -> List[dict]:
    """Return the current test record's successes followed by the records of each saved report."""
    records = list(test_record_instance.test_record_list)
    for path in report_paths or ():
        records.extend(load_report_records(path))
    return records


def build_openapi(report_paths: Optional[Sequence[str]] = None, title: str = DEFAULT_SPEC_TITLE,
                  version: str = DEFAULT_SPEC_VERSION) -> dict:
    """Return an OpenAPI document inferred from the current test record plus each saved report."""
    return records_to_openapi(collect_records(report_paths), title=title, version=version)


def export_openapi(output_path: str, report_paths: Optional[Sequence[str]] = None,
                   title: str = DEFAULT_SPEC_TITLE, version: str = DEFAULT_SPEC_VERSION) -> str:
    """
    Write the document from :func:`build_openapi` to ``output_path`` as UTF-8 JSON.

    :return: the path written.
    """
    spec = build_openapi(report_paths, title=title, version=version)
    Path(output_path).write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(output_path)
