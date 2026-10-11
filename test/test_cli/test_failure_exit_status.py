"""A run in which something failed ends with a non-zero exit status, from both command lines.

The executor records a failed action and runs the next one, and a failed request is only kept in
the test record, so ``python -m je_api_testka --execute_file`` and ``apitestka run`` used to end
with status 0 whatever happened. TestPioneer's ``parallel_run`` and a CI job read that status.
"""
import json
import os
import subprocess  # nosec B404 - the CLI is exercised as a real child process
import sys
from pathlib import Path

import pytest

from je_api_testka.cli.cli_common import FailureCount
from je_api_testka.cli.cli_main import main
from je_api_testka.utils.executor.action_executor import execute_action, executor
from je_api_testka.utils.test_record.test_record_class import test_record_instance

REPO_ROOT = Path(__file__).resolve().parents[2]
# No command has this name, so binding the action raises.
RAISES = ["AT_no_such_command"]
# A request that cannot be sent does not raise: it is logged and kept in the failure record.
FAILED_REQUEST = ["AT_test_api_method", {"http_method": "get", "test_url": "not a url"}]


def _badge(target: Path) -> list:
    """A harmless action whose only effect is writing ``target``."""
    return ["AT_generate_badge", {"file_name": str(target)}]


def _write(path: Path, actions: list) -> str:
    path.write_text(json.dumps(actions), encoding="utf-8")
    return str(path)


def _run_module(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    """Run ``python -m je_api_testka`` from this checkout."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(REPO_ROOT), env.get("PYTHONPATH")]))
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(  # nosec B603 - fixed interpreter, test-controlled arguments
        [sys.executable, "-m", "je_api_testka", *args],
        cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", timeout=300, check=False,
    )


class TestFailureCount:
    def test_an_action_that_raises_is_counted(self):
        with FailureCount() as count:
            execute_action([RAISES, RAISES])
        assert count.failed == 2

    def test_a_request_kept_in_the_failure_record_is_counted(self):
        with FailureCount() as count:
            execute_action([FAILED_REQUEST])
        assert count.failed == 1
        assert len(test_record_instance.error_record_list) == 1

    def test_only_what_fails_inside_the_block_is_counted(self):
        test_record_instance.error_record_list.append([{}, "earlier"])
        with FailureCount() as count:
            execute_action([RAISES])
        assert count.failed == 1

    def test_nothing_failed_is_zero(self, tmp_path):
        with FailureCount() as count:
            execute_action([_badge(tmp_path / "badge.json")])
        assert count.failed == 0

    def test_the_executor_gets_its_reporter_back(self):
        reporter = executor.settings.reporter
        with FailureCount():
            assert executor.settings.reporter is not reporter
        assert executor.settings.reporter is reporter

    def test_the_reporter_comes_back_when_the_block_raises(self):
        reporter = executor.settings.reporter
        with pytest.raises(RuntimeError), FailureCount():
            raise RuntimeError("stopped")
        assert executor.settings.reporter is reporter


class TestRunSubcommand:
    def test_a_run_without_failures_returns_0(self, tmp_path):
        assert main(["run", _write(tmp_path / "ok.json", [_badge(tmp_path / "badge.json")])]) == 0

    def test_an_action_that_raises_returns_1(self, tmp_path):
        assert main(["run", _write(tmp_path / "bad.json", [RAISES])]) == 1

    def test_a_failed_request_returns_1(self, tmp_path):
        assert main(["run", _write(tmp_path / "bad.json", [FAILED_REQUEST])]) == 1

    def test_a_directory_with_one_failing_file_returns_1(self, tmp_path):
        _write(tmp_path / "a_ok.json", [_badge(tmp_path / "badge.json")])
        _write(tmp_path / "b_bad.json", [RAISES])
        assert main(["run", str(tmp_path)]) == 1


class TestModuleCommandLine:
    @pytest.mark.parametrize("flag", ["-e", "--execute_file"])
    def test_an_action_that_raises_exits_1(self, tmp_path, flag):
        result = _run_module(tmp_path, flag, _write(tmp_path / "bad.json", [RAISES]))
        assert result.returncode == 1
        assert "1 action(s) failed" in result.stderr

    def test_a_failed_request_exits_1(self, tmp_path):
        result = _run_module(tmp_path, "--execute_file", _write(tmp_path / "bad.json", [FAILED_REQUEST]))
        assert result.returncode == 1
        assert "1 action(s) failed" in result.stderr

    def test_the_actions_after_a_failed_one_still_run(self, tmp_path):
        target = tmp_path / "badge.json"
        result = _run_module(tmp_path, "--execute_file", _write(tmp_path / "mixed.json", [RAISES, _badge(target)]))
        assert result.returncode == 1
        assert target.exists(), result.stdout + result.stderr

    def test_a_directory_with_one_failing_file_exits_1(self, tmp_path):
        actions = tmp_path / "actions"
        actions.mkdir()
        _write(actions / "a_ok.json", [_badge(tmp_path / "badge.json")])
        _write(actions / "b_bad.json", [RAISES])
        assert _run_module(tmp_path, "--execute_dir", str(actions)).returncode == 1

    def test_a_run_without_failures_still_exits_0(self, tmp_path):
        target = tmp_path / "badge.json"
        result = _run_module(tmp_path, "--execute_file", _write(tmp_path / "ok.json", [_badge(target)]))
        assert result.returncode == 0, result.stderr
        assert target.exists()
