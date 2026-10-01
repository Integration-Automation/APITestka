"""
Run a LoadDensity load test from APITestka and judge its summary.

LoadDensity is started as ``python -m je_load_density --execute_file <file>``
(its documented, contract-tested CLI), so its gevent monkey patching never
touches the APITestka process. The action file ends with
``LD_generate_summary_report``, and the run is judged from that summary,
because LoadDensity exits with 0 even when an action fails:

* no summary, or fewer requests than ``min_requests``, fails the run;
* ``max_failure_rate`` (0 to 1) and ``max_p95_ms`` are optional limits.

``je_load_density`` must be installed for the interpreter that runs it
(``python``, the current interpreter by default).
"""
from __future__ import annotations

import importlib.util
import json
import os

# LoadDensity runs out of process by design; argv is a fixed list built here and no shell is used.
import subprocess  # noqa: S404
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Mapping, Optional

from je_api_testka.integrations.load_density import LOAD_DENSITY_KEY
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

LOAD_DENSITY_MODULE: str = "je_load_density"
LOAD_DENSITY_MISSING: str = "je_load_density is not installed. Install with `pip install je_load_density`."
SUMMARY_NAME: str = "apitestka-load-summary"
ACTION_FILE_NAME: str = "apitestka-load-test.json"
TIMEOUT_MARGIN_SECONDS: int = 120
_OUTPUT_TAIL: int = 2000


@dataclass
class LoadThresholds:
    """Pass/fail limits applied to the LoadDensity summary."""

    max_failure_rate: Optional[float] = None
    max_p95_ms: Optional[float] = None
    min_requests: int = 1


@dataclass
class LoadRunResult:
    """What a load test run produced and why it failed, if it did."""

    returncode: int
    summary: dict = field(default_factory=dict)
    problems: List[str] = field(default_factory=list)
    work_dir: str = ""

    @property
    def ok(self) -> bool:
        """True when the run produced a summary within every threshold."""
        return not self.problems

    def to_dict(self) -> dict:
        """JSON-ready form: ``ok``, ``problems``, ``summary``, ``returncode`` and ``work_dir``."""
        return {"ok": self.ok, "problems": self.problems, "summary": self.summary,
                "returncode": self.returncode, "work_dir": self.work_dir}


def _with_summary_step(load_test: Mapping[str, object], summary_base: Path) -> dict:
    actions = list(load_test.get(LOAD_DENSITY_KEY) or [])
    actions.append(["LD_generate_summary_report", {"report_name": str(summary_base)}])
    return {LOAD_DENSITY_KEY: actions}


def _timeout_for(load_test: Mapping[str, object]) -> float:
    longest = [int(kwargs.get("test_time") or 0) for name, kwargs in (load_test.get(LOAD_DENSITY_KEY) or [])
               if name == "LD_start_test" and isinstance(kwargs, dict)]
    return float(sum(longest) + TIMEOUT_MARGIN_SECONDS)


def check_summary(summary: Mapping[str, object], thresholds: LoadThresholds) -> List[str]:
    """Return why ``summary`` breaks ``thresholds`` (empty when it does not)."""
    totals = summary.get("totals") or {}
    latency = summary.get("latency_overall") or {}
    problems: List[str] = []
    requests = int(totals.get("requests", 0))
    if requests < thresholds.min_requests:
        problems.append(f"{requests} requests ran, fewer than {thresholds.min_requests}")
    failure_rate = float(totals.get("failure_rate", 0.0))
    if thresholds.max_failure_rate is not None and failure_rate > thresholds.max_failure_rate:
        problems.append(f"failure rate {failure_rate:.2%} is above {thresholds.max_failure_rate:.2%}")
    p95 = float(latency.get("p95_ms", 0.0))
    if thresholds.max_p95_ms is not None and p95 > thresholds.max_p95_ms:
        problems.append(f"p95 latency {p95:.1f} ms is above {thresholds.max_p95_ms} ms")
    return problems


def _launch(python: str, action_file: Path, timeout: float) -> subprocess.CompletedProcess:
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-audit.dangerous-subprocess-use-audit
    return subprocess.run(  # noqa: S603
        [python, "-m", LOAD_DENSITY_MODULE, "--execute_file", str(action_file)],
        cwd=str(action_file.parent), env=environment, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout, check=False,
    )


def run_load_test(load_test: Mapping[str, object], thresholds: Optional[LoadThresholds] = None,
                  python: Optional[str] = None, work_dir: Optional[str] = None,
                  timeout: Optional[float] = None) -> LoadRunResult:
    """
    Run LoadDensity action JSON (from :func:`build_load_test`) and judge the summary.

    :param python: interpreter with ``je_load_density`` installed (default: this one).
    :param work_dir: folder for the action file and the summary (default: a new temporary folder, kept).
    :param timeout: seconds before the run is stopped (default: the tests' ``test_time`` plus two minutes).
    :raises APITesterException: when the current interpreter is used and ``je_load_density`` is missing.
    """
    interpreter = python or sys.executable
    if python is None and importlib.util.find_spec(LOAD_DENSITY_MODULE) is None:
        raise APITesterException(LOAD_DENSITY_MISSING)
    folder = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix="apitestka-load-"))
    folder.mkdir(parents=True, exist_ok=True)
    summary_base = (folder / SUMMARY_NAME).resolve()
    action_file = folder / ACTION_FILE_NAME
    action_file.write_text(json.dumps(_with_summary_step(load_test, summary_base), indent=2, ensure_ascii=False),
                           encoding="utf-8")
    try:
        completed = _launch(interpreter, action_file, timeout or _timeout_for(load_test))
    except subprocess.TimeoutExpired as error:
        return LoadRunResult(-1, problems=[f"LoadDensity did not finish within {error.timeout} s"],
                             work_dir=str(folder))
    result = LoadRunResult(completed.returncode, work_dir=str(folder))
    summary_file = summary_base.with_suffix(".json")
    if not summary_file.exists():
        output = (completed.stderr or completed.stdout or "")[-_OUTPUT_TAIL:]
        result.problems.append(f"LoadDensity wrote no summary (exit code {completed.returncode}): {output}")
        return result
    result.summary = json.loads(summary_file.read_text(encoding="utf-8"))
    result.problems.extend(check_summary(result.summary, thresholds or LoadThresholds()))
    apitestka_logger.info(f"load test in {folder}: {'ok' if result.ok else result.problems}")
    return result
