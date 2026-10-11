"""Tests for per-endpoint latency history, anomaly detection, the trend report and their entry points."""
from __future__ import annotations

import json

import pytest

from je_api_testka.cli.cli_main import main
from je_api_testka.spec.path_templates import generalize_path
from je_api_testka.utils.exception.exceptions import APIAssertException, APITesterException
from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.generate_report.latency_trends import (
    AnomalyPolicy,
    assert_no_latency_anomalies,
    detect_latency_anomalies,
    endpoint_history,
    endpoint_key,
    endpoint_stats,
    judge,
    record_endpoint_latencies,
)
from je_api_testka.utils.generate_report.trend_report import render_trend_report, sparkline
from je_api_testka.utils.test_record.test_record_class import test_record_instance

BASE = "https://api.invalid"


def _run(db: str, latencies_ms: dict, label: str = "") -> dict:
    """Record one run in which each URL answered in the given milliseconds."""
    test_record_instance.clean_record()
    for url, milliseconds in latencies_ms.items():
        test_record_instance.test_record_list.append(
            {"request_url": f"{BASE}{url}", "request_method": "GET", "request_time_sec": milliseconds / 1000})
    result = record_endpoint_latencies(db, label)
    test_record_instance.clean_record()
    return result


@pytest.mark.parametrize(("path", "expected"), [
    ("/users/42/orders/7", "/users/{id}/orders/{id2}"),
    ("/items/3f2504e0-4f89-11d3-9a0c-0305e82c3301", "/items/{id}"),
    ("/blobs/0123456789abcdef", "/blobs/{id}"),
    ("/v1/items/latest", "/v1/items/latest"),
    ("/", "/"),
])
def test_generalize_path(path, expected):
    assert generalize_path(path) == expected


def test_endpoint_key_prefers_openapi_templates():
    record = {"request_url": f"{BASE}/items/latest?x=1", "request_method": "post"}
    assert endpoint_key(record) == "POST /items/latest"
    assert endpoint_key(record, ["/items/{sku}"]) == "POST /items/{sku}"
    assert endpoint_key({"request_method": "GET"}) is None


def test_endpoint_stats_groups_and_skips_untimed():
    records = [{"request_url": f"{BASE}/items/{n}", "request_time_sec": n / 100} for n in range(1, 5)]
    records.append({"request_url": f"{BASE}/items/9"})
    stats = endpoint_stats(records)
    assert len(stats) == 1
    assert (stats[0].endpoint, stats[0].sample_count, stats[0].max_ms) == ("GET /items/{id}", 4, 40.0)
    assert stats[0].mean_ms == pytest.approx(25.0)


def test_record_and_history_include_saved_reports(tmp_path):
    db = str(tmp_path / "trend.sqlite")
    report = tmp_path / "run_success.json"
    report.write_text(json.dumps({"Success_Test1": {
        "request_url": f"{BASE}/ping", "request_method": "GET", "request_time_sec": "0.012"}}), encoding="utf-8")
    result = record_endpoint_latencies(db, "build-1", [str(report)])
    history = endpoint_history(db)
    assert result["endpoints"] == 1
    assert history["GET /ping"][0]["run_label"] == "build-1"
    assert history["GET /ping"][0]["p95_ms"] == pytest.approx(12.0)
    assert endpoint_history(str(tmp_path / "missing.sqlite")) == {}


POLICY = AnomalyPolicy(min_history=5)


@pytest.mark.parametrize(("values", "status"), [
    ([100, 100, 100], "insufficient_history"),
    ([100, 104, 98, 102, 101, 99, 103], "ok"),
    ([100, 104, 98, 102, 101, 99, 180], "anomaly"),
    ([100, 100, 100, 100, 100, 130], "anomaly"),
    ([2, 2, 2, 2, 2, 4], "ok"),
    ([100, 104, 98, 102, 101, 99, 40], "ok"),
    ([100, 150, 60, 140, 70, 130, 170], "ok"),
])
def test_judge(values, status):
    assert judge("GET /x", [float(v) for v in values], POLICY).status == status


def test_judge_uses_only_the_window():
    verdict = judge("GET /x", [500.0] * 10 + [100.0] * 5 + [100.0], AnomalyPolicy(window=5, min_history=5))
    assert (verdict.baseline_median, verdict.history, verdict.status) == (100.0, 5, "ok")


def test_detection_judges_endpoints_of_the_latest_run_only(tmp_path):
    db = str(tmp_path / "trend.sqlite")
    for _ in range(6):
        _run(db, {"/items/1": 100, "/gone": 50})
    _run(db, {"/items/2": 200})
    verdicts = detect_latency_anomalies(db, {"min_history": 5})
    assert [(v.endpoint, v.status) for v in verdicts] == [("GET /items/{id}", "anomaly")]
    with pytest.raises(APIAssertException, match="GET /items/\\{id\\} p95_ms 200.0 ms vs median 100.0 ms"):
        assert_no_latency_anomalies(db, {"min_history": 5})


@pytest.mark.parametrize("policy", [{"metric": "p42"}, {"window": 3, "min_history": 4}, {"unknown": 1}])
def test_bad_policy(policy, tmp_path):
    with pytest.raises(APITesterException):
        detect_latency_anomalies(str(tmp_path / "t.sqlite"), policy)


def test_report_escapes_and_marks_anomalies(tmp_path):
    db = str(tmp_path / "trend.sqlite")
    for _ in range(5):
        _run(db, {"/<script>": 10})
    _run(db, {"/<script>": 90})
    page = render_trend_report(db)
    assert "&lt;script&gt;" in page and "<script>" not in page
    assert 'class="anomaly"' in page and "#cf222e" in page
    assert "No runs recorded yet." in render_trend_report(str(tmp_path / "empty.sqlite"))
    assert sparkline([]) == ""


def test_executor_commands(tmp_path):
    db = str(tmp_path / "trend.sqlite")
    for _ in range(5):
        _run(db, {"/a": 10})
    test_record_instance.test_record_list.append({"request_url": f"{BASE}/a", "request_time_sec": 0.01})
    record = execute_action([
        ["AT_record_endpoint_latencies", {"db_path": db, "run_label": "ci"}],
        ["AT_detect_latency_anomalies", {"db_path": db}],
        ["AT_assert_no_latency_anomalies", {"db_path": db}],
        ["AT_generate_trend_report", {"output_path": str(tmp_path / "t.html"), "db_path": db}],
    ])
    values = list(record.values())
    assert values[1] == [{"endpoint": "GET /a", "metric": "p95_ms", "latest": 10.0, "baseline_median": 10.0,
                          "robust_z": None, "history": 5, "status": "ok"}]
    assert (tmp_path / "t.html").exists()


def test_cli_record_check_report(tmp_path, capsys):
    db = str(tmp_path / "trend.sqlite")
    report = tmp_path / "run_success.json"
    spec = tmp_path / "openapi.json"
    spec.write_text(json.dumps({"paths": {"/items/{sku}": {}}}), encoding="utf-8")
    for milliseconds in (100, 101, 99, 100, 102, 400):
        report.write_text(json.dumps([{"request_url": f"{BASE}/items/a1", "request_method": "GET",
                                       "request_time_sec": milliseconds / 1000}]), encoding="utf-8")
        assert main(["trend", "--db", db, "record", "--report", str(report), "--openapi", str(spec)]) == 0
    capsys.readouterr()
    assert main(["trend", "--db", db, "check"]) == 1
    assert "[anomaly] GET /items/{sku}: 400.0 ms" in capsys.readouterr().out
    assert main(["trend", "--db", db, "check", "--threshold", "1000", "--min-increase", "5", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["status"] == "ok"
    assert main(["trend", "--db", db, "report", "-o", str(tmp_path / "t.html")]) == 0
    assert "GET /items/{sku}" in (tmp_path / "t.html").read_text(encoding="utf-8")


def test_cli_usage_errors(tmp_path):
    db = str(tmp_path / "trend.sqlite")
    assert main(["trend", "--db", db, "record"]) == 2
    assert main(["trend", "--db", db, "record", "--report", "x.json", "--openapi", str(tmp_path / "no.json")]) == 2
    assert main(["trend", "--db", db, "check", "--window", "2"]) == 2
