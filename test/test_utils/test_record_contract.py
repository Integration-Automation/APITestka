import asyncio
import builtins
import json
from datetime import timedelta

import httpx
import pytest

pytest.importorskip("je_action_core.request_context", reason="coordinated ActionCore request-record release")

from je_api_testka.httpx_wrapper.async_httpx_method import test_api_method_httpx_async as run_async
from je_api_testka.httpx_wrapper.httpx_method import test_api_method_httpx as run_httpx
from je_api_testka.requests_wrapper.request_method import test_api_method_requests as run_requests
from je_api_testka.utils.test_record.contract import from_legacy_record
from je_api_testka.utils.test_record.run_context import RunContext, use_run_context
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def context(engine="requests"):
    return RunContext(source="apitestka", phase="functional", engine=engine)


@pytest.mark.parametrize("runner,engine", [(run_requests, "requests"), (run_httpx, "httpx")])
def test_real_response_has_shared_record_and_unchanged_native_return(mock_url, runner, engine):
    run = context(engine)
    with use_run_context(run):
        native = runner("get", mock_url + "/get", result_check_dict={"status_code": 200})
    assert native["response"].status_code == 200
    assert native["response_data"]["request_method"] == "GET"
    assert len(test_record_instance.test_record_list) == 1
    record = json.loads(run.to_json())[0]
    assert record["status_code"] == 200
    assert record["outcome"] == "passed"
    assert record["source"] == "apitestka"
    assert record["engine"] == engine
    assert record["response_time_ms"] >= 0
    assert record["assertions"] == [{"type": "status_code", "passed": True}]


@pytest.mark.parametrize("runner,engine", [(run_requests, "requests"), (run_httpx, "httpx")])
def test_http_failure_preserves_response_status_and_legacy_pair(mock_url, runner, engine):
    run = context(engine)
    with use_run_context(run):
        assert runner("get", mock_url + "/missing") is None
    assert len(test_record_instance.error_record_list[0]) == 2
    result = run.snapshot()[0]
    assert result["status_code"] == 404
    assert result["outcome"] == "failed"
    assert result["error"]["kind"] == "http_status"
    assert result["response_length"] > 0


def test_assertion_failure_is_distinct_from_transport_error(mock_url):
    run = context()
    with use_run_context(run):
        assert run_requests("get", mock_url + "/get", result_check_dict={"status_code": 201}) is None
    result = run.snapshot()[0]
    assert result["status_code"] == 200
    assert result["outcome"] == "failed"
    assert result["error"]["kind"] == "assertion"
    assert result["assertions"][0]["passed"] is False


def test_success_recording_disabled_does_not_emit_canonical_result(mock_url):
    run = context()
    with use_run_context(run):
        assert run_requests("get", mock_url + "/get", record_request_info=False) is not None
    assert run.snapshot() == []
    assert test_record_instance.test_record_list == []


def test_async_httpx_uses_same_context_and_native_result(mock_url):
    run = context("httpx_async")

    async def execute():
        with use_run_context(run):
            return await run_async("get", mock_url + "/get")

    result = asyncio.run(execute())
    assert result["response"].status_code == 200
    assert run.snapshot()[0]["engine"] == "httpx_async"
    assert run.snapshot()[0]["outcome"] == "passed"


def test_legacy_failure_pair_preserves_unknown_measurements():
    result = from_legacy_record([{"http_method": "post", "test_url": "http://localhost/"}, "refused"], context())
    assert result["request_method"] == "POST"
    assert result["status_code"] is None
    assert result["response_time_ms"] is None
    assert result["error"]["message"] == "refused"


def test_invalid_legacy_failure_reports_location():
    with pytest.raises(ValueError, match="record"):
        from_legacy_record(["bad"], context())


def test_empty_timeout_message_keeps_measured_failure(monkeypatch):
    from je_api_testka.requests_wrapper import request_method
    from je_api_testka.utils.test_record import request_capture

    def fail(*args, **kwargs):
        raise TimeoutError()

    monkeypatch.setattr(request_method, "send_requests", fail)
    ticks = iter([1.0, 1.025])
    monkeypatch.setattr(request_capture, "monotonic", lambda: next(ticks))
    run = context()
    with use_run_context(run):
        assert run_requests("get", "http://localhost/") is None
    result = run.snapshot()[0]
    assert result["status_code"] is None
    assert result["response_time_ms"] == pytest.approx(25)
    assert result["error"] == {"kind": "timeout", "message": "TimeoutError()"}


def test_parallel_async_scopes_keep_responses_separate(monkeypatch):
    from je_api_testka.httpx_wrapper import async_httpx_method

    async def send(method, test_url, **kwargs):
        await asyncio.sleep(0)
        response = httpx.Response(200, json={"url": test_url}, request=httpx.Request(method, test_url))
        response.elapsed = timedelta(milliseconds=1)
        return response

    monkeypatch.setattr(async_httpx_method, "send_httpx_requests_async", send)
    first, second = context("httpx_async"), context("httpx_async")

    async def execute(run, url):
        with use_run_context(run):
            await run_async("get", url)

    async def both():
        await asyncio.gather(execute(first, "http://first/"), execute(second, "http://second/"))

    asyncio.run(both())
    assert [item["request_url"] for item in first.snapshot()] == ["http://first/"]
    assert [item["request_url"] for item in second.snapshot()] == ["http://second/"]


def test_payload_import_is_explicit_and_masks_headers():
    data = {"request_method": "GET", "request_url": "http://localhost/", "status_code": 200,
            "headers": {"Authorization": "secret", "Content-Type": "text/plain"},
            "text": "ok", "content": b"ok", "elapsed": timedelta(milliseconds=12)}
    ordinary = from_legacy_record(data, context())
    assert "text" not in ordinary and "headers" not in ordinary
    detailed = from_legacy_record(data, context(), capture_payload=True)
    assert detailed["headers"] == {"Authorization": "[REDACTED]", "Content-Type": "text/plain"}
    assert detailed["content_base64"] == "b2s="
    assert detailed["response_time_ms"] == 12


def test_earlier_core_keeps_legacy_capture_optional(monkeypatch):
    from je_api_testka.utils.test_record.contract import get_optional_run_context

    original_import = builtins.__import__

    def earlier_core(name, *args, **kwargs):
        if name == "je_action_core.request_context":
            raise ModuleNotFoundError("missing context", name=name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", earlier_core)
    assert get_optional_run_context() is None
