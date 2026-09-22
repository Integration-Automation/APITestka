"""Contract test for the legacy CLI flags that other repositories call.

PyBreeze starts ``python -m je_api_testka --execute_str <json>`` (JSON-encoded a second
time on Windows, see ``pybreeze/extend/process_executor/python_task_process_manager.py``)
and ``--execute_file <path>``; TestPioneer's ``parallel_run`` starts
``--execute_file <path>``; PyBreeze's "create project" menu calls
``je_api_testka.create_project_dir()`` in process. Nothing on the consumer side tests
these, so this file does: renaming or removing a flag, or dropping the second
JSON decode on Windows, breaks them (workspace item X-7).
"""
import json
import os
import subprocess  # nosec B404 - the CLI is exercised as a real child process
import sys
from pathlib import Path

import pytest

import je_api_testka

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "je_api_testka"
IS_WINDOWS = sys.platform in ("win32", "cygwin", "msys")


def _run_cli(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    """Run ``python -m PACKAGE`` from this checkout; *cwd* catches any log file it writes."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(REPO_ROOT), env.get("PYTHONPATH")]))
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(  # nosec B603 - fixed interpreter, test-controlled arguments
        [sys.executable, "-m", PACKAGE, *args],
        cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8",
        timeout=300, check=False,
    )


def _pybreeze_execute_str(actions: list) -> str:
    """Encode *actions* the way PyBreeze's ``start_test_process`` does."""
    payload = json.dumps(actions)
    return json.dumps(payload) if IS_WINDOWS else payload


def _actions(target: Path) -> list:
    """A harmless action list whose only effect is writing *target*."""
    return [["AT_generate_badge", {"file_name": str(target)}]]


def _assert_ran(result: subprocess.CompletedProcess, target: Path) -> None:
    assert result.returncode == 0, result.stderr
    assert target.exists(), result.stdout + result.stderr


@pytest.mark.parametrize("flag", ["-e", "--execute_file"])
def test_execute_file(tmp_path, flag):
    target = tmp_path / "badge.json"
    action_file = tmp_path / "actions.json"
    action_file.write_text(json.dumps(_actions(target)), encoding="utf-8")
    _assert_ran(_run_cli(tmp_path, flag, str(action_file)), target)


@pytest.mark.parametrize("flag", ["-d", "--execute_dir"])
def test_execute_dir(tmp_path, flag):
    target = tmp_path / "badge.json"
    action_dir = tmp_path / "actions"
    action_dir.mkdir()
    (action_dir / "actions.json").write_text(json.dumps(_actions(target)), encoding="utf-8")
    _assert_ran(_run_cli(tmp_path, flag, str(action_dir)), target)


def test_execute_str_as_pybreeze_sends_it(tmp_path):
    target = tmp_path / "badge.json"
    _assert_ran(_run_cli(tmp_path, "--execute_str", _pybreeze_execute_str(_actions(target))), target)


@pytest.mark.parametrize("flag", ["-c", "--create_project"])
def test_create_project(tmp_path, flag):
    project = tmp_path / "project"
    result = _run_cli(tmp_path, flag, str(project))
    assert result.returncode == 0, result.stderr
    assert project.is_dir(), result.stdout + result.stderr
    assert any(project.rglob("*.json")), result.stdout + result.stderr


def test_no_flag_exits_non_zero(tmp_path):
    assert _run_cli(tmp_path).returncode != 0


def test_create_project_dir_is_exported():
    assert callable(je_api_testka.create_project_dir)
