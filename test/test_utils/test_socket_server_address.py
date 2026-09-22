"""The socket server binds what it is given; only its command line reads argv."""
import socket
import subprocess  # nosec B404 - runs this package's own module with fixed arguments
import sys
import time

import pytest

from je_api_testka.utils.socket_server import api_testka_socket_server as server_module
from je_api_testka.utils.socket_server.api_testka_socket_server import (
    _parse_cli_address,
    start_apitestka_socket_server,
)


def test_command_line_arguments_do_not_rebind_the_server(monkeypatch):
    # A host program run as "prog.py some_arg" used to have "some_arg" taken as the bind host.
    monkeypatch.setattr("sys.argv", ["prog.py", "not-a-host"])
    server = start_apitestka_socket_server("127.0.0.1", 0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.parametrize("argv, expected", [
    ([], ("localhost", 9939)),
    (["0.0.0.0"], ("0.0.0.0", 9939)),  # nosec B104 - parsing only, nothing is bound
    (["127.0.0.1", "9000"], ("127.0.0.1", 9000)),
])
def test_cli_address(argv, expected):
    assert _parse_cli_address(argv) == expected


def test_cli_rejects_a_non_numeric_port():
    with pytest.raises(SystemExit):
        _parse_cli_address(["127.0.0.1", "http"])


def test_main_starts_the_server_on_the_parsed_address(monkeypatch):
    calls = []

    class _Stopped:
        close_flag = True

    def fake_start(host, port):
        calls.append((host, port))
        return _Stopped()

    monkeypatch.setattr(server_module, "start_apitestka_socket_server", fake_start)
    server_module.main(["127.0.0.1", "9123"])
    assert calls == [("127.0.0.1", 9123)]


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _send_quit(port, deadline):
    while True:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1) as client:
                client.sendall(b"quit_server")
            return
        except OSError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.1)


def test_documented_command_line_runs_until_quit_server():
    port = _free_port()
    process = subprocess.Popen(  # nosec B603 - fixed argument list, no shell
        [sys.executable, "-m", "je_api_testka.utils.socket_server.api_testka_socket_server",
         "127.0.0.1", str(port)])
    try:
        _send_quit(port, time.monotonic() + 30)
        assert process.wait(timeout=30) == 0
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
