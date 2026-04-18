import logging
import socket
import threading
import time

import pytest
from flask import Flask, jsonify, request
from werkzeug.serving import make_server

from je_api_testka.utils.test_record.test_record_class import test_record_instance


MOCK_HOST = "127.0.0.1"
MOCK_PORT = 8091
MOCK_BASE_URL = f"http://{MOCK_HOST}:{MOCK_PORT}"


def _build_mock_app() -> Flask:
    app = Flask(__name__)

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
