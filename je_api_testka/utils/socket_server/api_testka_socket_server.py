"""
The APITestka socket server (port 9939): je_action_core's plain TCP action server running ``execute_action``.

A client sends one JSON action list per connection and reads one line per result, then
``Return_Data_Over_JE``; ``quit_server`` stops the server.
"""
import argparse
import time

from je_action_core import ActionRequestHandler, ActionTCPServer, SocketServerSettings, start_action_socket_server

from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

_DEFAULT_HOST = "localhost"
_DEFAULT_PORT = 9939
_QUIT_POLL_SECONDS = 0.2
_SETTINGS = SocketServerSettings(execute=execute_action, log_info=apitestka_logger.info,
                                 log_error=apitestka_logger.error)

# The names this module has always exported.
TCPServer = ActionTCPServer
TCPServerHandler = ActionRequestHandler


def start_apitestka_socket_server(host: str = _DEFAULT_HOST, port: int = _DEFAULT_PORT) -> ActionTCPServer:
    """
    啟動 TCP Socket 伺服器
    Start TCP socket server

    Binds exactly ``host`` and ``port``; the command line is read only by :func:`main`.

    :param host: 伺服器主機 / Server host
    :param port: 伺服器埠號 / Server port
    :return: TCPServer 實例 / TCPServer instance
    """
    apitestka_logger.info(
        f"api_testka_socket_server.py start_apitestka_socket_server host: {host} port: {port}"
    )
    return start_action_socket_server(host, port, _SETTINGS)


def _parse_cli_address(argv: list[str] | None) -> tuple[str, int]:
    """Host and port from ``[host [port]]`` command-line arguments (``None`` reads ``sys.argv``)."""
    parser = argparse.ArgumentParser(
        prog="python -m je_api_testka.utils.socket_server.api_testka_socket_server",
        description="Run the APITestka socket server until a client sends quit_server.")
    parser.add_argument("host", nargs="?", default=_DEFAULT_HOST)
    parser.add_argument("port", nargs="?", type=int, default=_DEFAULT_PORT)
    args = parser.parse_args(argv)
    return args.host, args.port


def main(argv: list[str] | None = None) -> None:
    """Start the server from the command line and block until a client sends ``quit_server``."""
    host, port = _parse_cli_address(argv)
    server = start_apitestka_socket_server(host, port)
    while not server.close_flag:
        time.sleep(_QUIT_POLL_SECONDS)


if __name__ == "__main__":
    main()
