import logging
import os
import socket
import threading
import time

import pytest
from flask import Flask, jsonify, request
from werkzeug.serving import make_server

from je_api_testka import (
    execute_action,
    generate_html, generate_html_report,
    generate_json, generate_json_report,
    generate_xml, generate_xml_report,
)
from je_api_testka.utils.test_record.test_record_class import test_record_instance


MOCK_HOST = "127.0.0.1"
MOCK_PORT = 8091
# Local in-process mock for the test suite; HTTPS not applicable on a loopback test fixture.
MOCK_BASE_URL = f"http://{MOCK_HOST}:{MOCK_PORT}"  # NOSONAR S5332


def _build_mock_app() -> Flask:
    # Test-only echo server: no form auth surface, CSRF not applicable.
    app = Flask(__name__)  # NOSONAR S4502

    def _echo_response():
        return jsonify({
            "args": request.args.to_dict(flat=True),
            "form": request.form.to_dict(flat=True),
            "headers": dict(request.headers),
            "url": request.url,
            "method": request.method,
        }), 200

    all_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    for path in ("/get", "/post", "/put", "/patch", "/delete"):
        app.add_url_rule(path, path, _echo_response, methods=all_methods)
    return app


class _MockServerThread(threading.Thread):
    def __init__(self, app: Flask, host: str, port: int) -> None:
        super().__init__(daemon=True)
        # werkzeug's server_bind calls socket.getfqdn(host), which on some
        # CI runners (notably macOS) hangs on reverse DNS for 127.0.0.1.
        # Temporarily bypass the lookup.
        original_getfqdn = socket.getfqdn
        socket.getfqdn = lambda name="": name or host
        try:
            self._server = make_server(host, port, app, threaded=True)
        finally:
            socket.getfqdn = original_getfqdn

    def run(self) -> None:
        self._server.serve_forever()

    def shutdown(self) -> None:
        self._server.shutdown()


def _wait_for_server(host: str, port: int, timeout_seconds: float = 5.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError(f"Mock server at {host}:{port} did not start within {timeout_seconds}s")


@pytest.fixture(scope="session", autouse=True)
def mock_server():
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    thread = _MockServerThread(_build_mock_app(), MOCK_HOST, MOCK_PORT)
    thread.start()
    _wait_for_server(MOCK_HOST, MOCK_PORT)
    yield MOCK_BASE_URL
    thread.shutdown()


@pytest.fixture(autouse=True)
def clean_test_records():
    """Clean test records before each test to avoid cross-test pollution."""
    test_record_instance.clean_record()
    yield
    test_record_instance.clean_record()


# ─── Shared HTTP-method test helpers ──────────────────────────────────

@pytest.fixture
def mock_url():
    """Base URL of the local mock HTTP server."""
    return MOCK_BASE_URL


@pytest.fixture
def assert_valid_response():
    """Return a callable that validates a successful response dict."""
    def _assert(response, expected_method=None):
        assert response is not None
        data = response.get("response_data")
        assert data is not None
        assert data.get("status_code") == 200
        assert data.get("text") is not None
        assert data.get("headers") is not None
        assert data.get("elapsed") is not None
        assert data.get("start_time") is not None
        assert data.get("end_time") is not None
        if expected_method:
            assert data.get("request_method") == expected_method
    return _assert


@pytest.fixture
def assert_get_extras():
    """Return a callable that asserts the GET-specific response fields."""
    def _assert(response):
        data = response["response_data"]
        assert data.get("content") is not None
        assert data.get("cookies") is not None
        assert data.get("request_url") is not None
        assert data.get("request_time_sec") >= 0
    return _assert


# ─── Shared report-generation test helpers ────────────────────────────

def _report_action_list(action_name: str) -> list:
    return [
        [action_name, {
            "http_method": "get", "test_url": f"{MOCK_BASE_URL}/get",
            "result_check_dict": {"status_code": 200},
            "timeout": 30,
        }],
        [action_name, {
            "http_method": "post", "test_url": f"{MOCK_BASE_URL}/post",
            "params": {"task": "new task"},
            "result_check_dict": {"status_code": 300},
            "timeout": 30,
        }],
    ]


@pytest.fixture
def run_report_actions():
    """Return a callable that executes the standard success+failure action pair."""
    def _run(action_name: str) -> None:
        execute_action(_report_action_list(action_name))
    return _run


@pytest.fixture
def run_report_suite(run_report_actions, tmp_path):
    """Run the full report-generation suite for a given executor action.

    Used by per-backend test files: they pick the action_name (e.g.
    ``AT_test_api_method``) and the suite verifies all six report flavors.
    """
    def _run(action_name: str) -> None:
        report_path = str(tmp_path / "test_report")

        run_report_actions(action_name)
        success_list, failure_list = generate_html()
        assert isinstance(success_list, list)
        assert isinstance(failure_list, list)
        assert len(success_list) > 0

        run_report_actions(action_name)
        generate_html_report(report_path)
        assert os.path.exists(report_path + ".html")

        run_report_actions(action_name)
        success_dict, failure_dict = generate_json()
        assert isinstance(success_dict, dict)
        assert isinstance(failure_dict, dict)
        assert len(success_dict) > 0

        run_report_actions(action_name)
        generate_json_report(report_path)
        assert os.path.exists(report_path + "_success.json")
        assert os.path.exists(report_path + "_failure.json")

        run_report_actions(action_name)
        success_xml, failure_xml = generate_xml()
        assert isinstance(success_xml, str)
        assert isinstance(failure_xml, str)
        assert "<xml_data>" in success_xml

        run_report_actions(action_name)
        generate_xml_report(report_path)
        assert os.path.exists(report_path + "_success.xml")
        assert os.path.exists(report_path + "_failure.xml")
    return _run
