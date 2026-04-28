"""
Pytest fixtures for APITestka.

Register the plugin via ``pytest_plugins = ["je_api_testka.pytest_plugin"]`` in
``conftest.py`` (or distribute it as an entry point).
"""
from __future__ import annotations

import threading
from typing import Iterator

import pytest

from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer
from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_FIXTURE_HOST: str = "127.0.0.1"
DEFAULT_FIXTURE_PORT: int = 0


@pytest.fixture
def apitestka_record():
    """Yield the global test record instance and clear it after the test."""
    yield test_record_instance
    test_record_instance.clean_record()


@pytest.fixture
def apitestka_clean_record():
    """Clear the global test record before and after the test."""
    test_record_instance.clean_record()
    yield
    test_record_instance.clean_record()


@pytest.fixture
def apitestka_mock_server(unused_tcp_port_factory) -> Iterator[FlaskMockServer]:
    """
    Start a fresh ``FlaskMockServer`` in a background thread on a random port.

    The fixture relies on ``pytest-asyncio`` style ``unused_tcp_port_factory``
    when available; otherwise port 0 lets the OS allocate.
    """
    port = unused_tcp_port_factory() if callable(unused_tcp_port_factory) else DEFAULT_FIXTURE_PORT
    server = FlaskMockServer(DEFAULT_FIXTURE_HOST, port)
    thread = threading.Thread(
        target=server.app.run,
        kwargs={"host": DEFAULT_FIXTURE_HOST, "port": port, "use_reloader": False},
        daemon=True,
    )
    thread.start()
    try:
        yield server
    finally:
        # Flask dev server has no clean shutdown hook from another thread;
        # the daemon thread will exit when the test process ends.
        pass
