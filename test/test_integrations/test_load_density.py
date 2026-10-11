"""Tests for the LoadDensity bridge: conversion, the out-of-process runner and its entry points."""
from __future__ import annotations

import json
import sys
import textwrap

import pytest

from je_api_testka.cli.cli_main import main
from je_api_testka.integrations import load_density_runner
from je_api_testka.integrations.load_density import (
    LoadProfile,
    actions_to_load_plan,
    build_load_test,
    records_to_load_plan,
)
from je_api_testka.integrations.load_density_commands import run_load_test_from, write_load_test
from je_api_testka.integrations.load_density_runner import LoadThresholds, check_summary, run_load_test
from je_api_testka.utils.exception.exceptions import APIAssertException, APITesterException
from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.test_record.test_record_class import test_record_instance

URL = "https://api.invalid/items?page=1"
ACTIONS = [
    ["AT_test_api_method", {"http_method": "POST", "test_url": URL, "json": {"a": 1}, "headers": {"X": "1"},
                            "timeout": 5, "result_check_dict": {"status_code": 201}, "tags": ["smoke"]}],
    ["AT_test_api_method_httpx", {"http_method": "get", "test_url": "https://api.invalid/", "params": {"q": "x"}}],
    ["AT_fake_uuid"],
    ["AT_test_api_method", {"http_method": "get", "test_url": "/relative"}],
    ["AT_test_api_method", ["get", URL]],
    "not an action",
]


def test_actions_become_tasks_and_the_rest_is_reported():
    plan = actions_to_load_plan({"api_testka": ACTIONS})
    assert plan.tasks == [
        {"method": "post", "request_url": URL, "name": "POST /items", "headers": {"X": "1"}, "json": {"a": 1},
         "timeout": 5, "assertions": [{"type": "status_code", "value": 201}]},
        {"method": "get", "request_url": "https://api.invalid/", "name": "GET /", "params": {"q": "x"}},
    ]
    assert len(plan.skipped) == 4
    assert any("absolute" in reason for reason in plan.skipped)


def test_records_become_tasks():
    plan = records_to_load_plan([
        {"request_url": URL, "request_method": "POST", "status_code": "201", "request_body": b'{"a": 1}'},
        {"request_url": URL, "request_method": "PUT", "status_code": 200, "request_body": "a=1"},
        {"status_code": 200},
    ])
    assert plan.tasks[0]["json"] == {"a": 1}
    assert plan.tasks[0]["assertions"] == [{"type": "status_code", "value": 201}]
    assert plan.tasks[1]["data"] == "a=1"
    assert plan.skipped == ["record without request_url"]


def test_build_load_test_shape():
    load_test = build_load_test([{"method": "get", "request_url": URL}], LoadProfile(user_count=3, test_time=2))
    name, kwargs = load_test["load_density"][0]
    assert name == "LD_start_test"
    assert kwargs == {"user_detail_dict": {"user": "fast_http_user"},
                      "tasks": {"mode": "sequence", "tasks": [{"method": "get", "request_url": URL}]},
                      "user_count": 3, "spawn_rate": 5, "test_time": 2}


@pytest.mark.parametrize("options", [{"user": "grpc_user"}, {"mode": "random"}, {"user_count": 0}])
def test_profile_validation(options):
    with pytest.raises(APITesterException):
        LoadProfile(**options)


def test_nothing_to_run_raises():
    with pytest.raises(APITesterException):
        build_load_test([], LoadProfile())


def test_check_summary_thresholds():
    summary = {"totals": {"requests": 10, "failure_rate": 0.2}, "latency_overall": {"p95_ms": 900.0}}
    assert check_summary(summary, LoadThresholds()) == []
    assert check_summary(summary, LoadThresholds(max_failure_rate=0.1, max_p95_ms=500, min_requests=11)) == [
        "10 requests ran, fewer than 11", "failure rate 20.00% is above 10.00%", "p95 latency 900.0 ms is above 500 ms"]


FAKE_MAIN = textwrap.dedent('''
    """Stand-in for `python -m je_load_density --execute_file FILE` (the LoadDensity CLI contract)."""
    import json, os, pathlib, sys, time
    path = pathlib.Path(sys.argv[sys.argv.index("--execute_file") + 1])
    document = json.loads(path.read_text(encoding="utf-8"))
    pathlib.Path("seen.json").write_text(json.dumps({"cwd": os.getcwd(), "document": document}), encoding="utf-8")
    behaviour = os.environ.get("FAKE_LD", "ok")
    if behaviour == "sleep":
        time.sleep(30)
    if behaviour == "crash":
        sys.exit(1)
    tasks = document["load_density"][0][1]["tasks"]["tasks"]
    failures = 1 if behaviour == "failures" else 0
    summary = {"totals": {"requests": 4 * len(tasks), "successes": 4 * len(tasks) - failures, "failures": failures,
                          "failure_rate": failures / (4 * len(tasks))},
               "latency_overall": {"count": 4 * len(tasks), "p50_ms": 5.0, "p90_ms": 8.0, "p95_ms": 9.0,
                                   "p99_ms": 9.5, "max_ms": 10.0},
               "per_name": {}}
    report = document["load_density"][-1]
    assert report[0] == "LD_generate_summary_report"
    pathlib.Path(report[1]["report_name"] + ".json").write_text(json.dumps(summary), encoding="utf-8")
''')


@pytest.fixture
def fake_load_density(tmp_path, monkeypatch):
    package = tmp_path / "fake_site" / "je_load_density"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "__main__.py").write_text(FAKE_MAIN, encoding="utf-8")
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "fake_site"))
    return tmp_path


def _load_test():
    return build_load_test([{"method": "get", "request_url": URL}], LoadProfile(test_time=1))


def test_runner_writes_the_file_runs_the_cli_and_reads_the_summary(fake_load_density):
    work = fake_load_density / "work"
    result = run_load_test(_load_test(), LoadThresholds(max_failure_rate=0.0), python=sys.executable,
                           work_dir=str(work))
    seen = json.loads((work / "seen.json").read_text(encoding="utf-8"))
    assert result.ok, result.problems
    assert result.summary["totals"]["requests"] == 4
    assert seen["document"]["load_density"][0][0] == "LD_start_test"
    assert result.to_dict()["returncode"] == 0


def test_runner_reports_threshold_breaches(fake_load_density, monkeypatch):
    monkeypatch.setenv("FAKE_LD", "failures")
    result = run_load_test(_load_test(), LoadThresholds(max_failure_rate=0.1), python=sys.executable,
                           work_dir=str(fake_load_density / "work"))
    assert result.problems == ["failure rate 25.00% is above 10.00%"]


def test_runner_without_summary_fails(fake_load_density, monkeypatch):
    monkeypatch.setenv("FAKE_LD", "crash")
    result = run_load_test(_load_test(), python=sys.executable, work_dir=str(fake_load_density / "work"))
    assert not result.ok
    assert result.problems[0].startswith("LoadDensity wrote no summary (exit code 1)")


def test_runner_timeout(fake_load_density, monkeypatch):
    monkeypatch.setenv("FAKE_LD", "sleep")
    result = run_load_test(_load_test(), python=sys.executable, work_dir=str(fake_load_density / "work"),
                           timeout=1)
    assert result.returncode == -1
    assert "did not finish" in result.problems[0]


def test_runner_needs_load_density_for_this_interpreter(monkeypatch):
    monkeypatch.setattr(load_density_runner.importlib.util, "find_spec", lambda name: None)
    with pytest.raises(APITesterException, match="pip install je_load_density"):
        run_load_test(_load_test())


def _action_file(tmp_path):
    path = tmp_path / "smoke.json"
    path.write_text(json.dumps(ACTIONS[:2]), encoding="utf-8")
    return str(path)


def test_write_load_test_and_executor(tmp_path):
    written = write_load_test(str(tmp_path / "out" / "load.json"), action_file=_action_file(tmp_path),
                              profile={"user_count": 2})
    assert json.loads((tmp_path / "out" / "load.json").read_text(encoding="utf-8"))["load_density"][0][1][
        "user_count"] == 2
    test_record_instance.test_record_list.append({"request_url": URL, "request_method": "GET", "status_code": 200})
    record = execute_action([["AT_write_load_test", {"output_path": str(tmp_path / "rec.json")}]])
    assert written.endswith("load.json")
    assert list(record.values()) == [str(tmp_path / "rec.json")]


def test_bad_profile_options(tmp_path):
    with pytest.raises(APITesterException):
        write_load_test(str(tmp_path / "x.json"), action_file=_action_file(tmp_path), profile={"users": 3})


def test_run_load_test_from_raises_on_failure(fake_load_density, tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_LD", "failures")
    with pytest.raises(APIAssertException, match="failure rate"):
        run_load_test_from(action_file=_action_file(tmp_path), profile={"test_time": 1},
                           thresholds={"max_failure_rate": 0.0}, python=sys.executable)
    monkeypatch.setenv("FAKE_LD", "ok")
    assert run_load_test_from(action_file=_action_file(tmp_path), python=sys.executable)["ok"] is True


def test_cli_convert_and_run(fake_load_density, tmp_path, capsys, monkeypatch):
    actions = _action_file(tmp_path)
    assert main(["load", "convert", "--actions", actions, "-o", str(tmp_path / "load.json"), "--users", "2"]) == 0
    assert main(["load", "run", "--actions", actions, "--time", "1", "--python", sys.executable,
                 "--max-p95-ms", "100", "--json"]) == 0
    assert json.loads(capsys.readouterr().out.split("\n", 1)[1])["ok"] is True
    monkeypatch.setenv("FAKE_LD", "failures")
    assert main(["load", "run", "--actions", actions, "--time", "1", "--python", sys.executable,
                 "--max-failure-rate", "0"]) == 1
    assert "FAIL: failure rate" in capsys.readouterr().out


def test_cli_usage_errors(tmp_path):
    assert main(["load", "convert", "-o", str(tmp_path / "x.json")]) == 2
    assert main(["load", "run"]) == 2
    empty = tmp_path / "empty.json"
    empty.write_text("[]", encoding="utf-8")
    assert main(["load", "convert", "--actions", str(empty), "-o", str(tmp_path / "x.json")]) == 1
