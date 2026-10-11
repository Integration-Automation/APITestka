"""
File-level LoadDensity steps for the executor (``AT_*``) and ``apitestka load``.

The requests come from an APITestka action file, or, without one, from the
current test record plus saved JSON reports. ``profile`` and ``thresholds``
are plain mappings (the JSON action form) for :class:`LoadProfile` and
:class:`LoadThresholds`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Optional, Sequence

from je_api_testka.integrations.load_density import (
    LoadPlan,
    LoadProfile,
    actions_to_load_plan,
    build_load_test,
    records_to_load_plan,
)
from je_api_testka.integrations.load_density_runner import LoadThresholds, run_load_test
from je_api_testka.spec.openapi_export import collect_records
from je_api_testka.utils.exception.exceptions import APIAssertException, APITesterException
from je_api_testka.utils.json.json_file.json_file import read_action_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def _options(kind: type, values: Optional[Mapping[str, object]]):
    try:
        return kind(**dict(values or {}))
    except TypeError as error:
        raise APITesterException(f"bad {kind.__name__} options {values!r}: {error}") from error


def load_plan(action_file: Optional[str] = None, report_paths: Optional[Sequence[str]] = None) -> LoadPlan:
    """Return the load plan for an action file, or for the current record plus saved reports."""
    if action_file:
        plan = actions_to_load_plan(read_action_json(action_file))
    else:
        plan = records_to_load_plan(collect_records(report_paths))
    for reason in plan.skipped:
        apitestka_logger.info(f"load plan skipped {reason}")
    return plan


def write_load_test(output_path: str, action_file: Optional[str] = None,
                    report_paths: Optional[Sequence[str]] = None,
                    profile: Optional[Mapping[str, object]] = None) -> str:
    """Write LoadDensity action JSON for the requests to ``output_path`` and return the path."""
    load_test = build_load_test(load_plan(action_file, report_paths).tasks, _options(LoadProfile, profile))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(load_test, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(target)


def run_load_test_from(action_file: Optional[str] = None, report_paths: Optional[Sequence[str]] = None,
                       profile: Optional[Mapping[str, object]] = None,
                       thresholds: Optional[Mapping[str, object]] = None, python: Optional[str] = None) -> dict:
    """
    Load test the requests with LoadDensity and return the run as a dict.

    :raises APIAssertException: with the problems when the run fails or breaks a threshold.
    """
    load_test = build_load_test(load_plan(action_file, report_paths).tasks, _options(LoadProfile, profile))
    result = run_load_test(load_test, _options(LoadThresholds, thresholds), python=python)
    if not result.ok:
        raise APIAssertException("load test failed: " + "; ".join(result.problems))
    return result.to_dict()
