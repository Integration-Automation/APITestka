import argparse
import json
import socketserver
import threading
import time

from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

_END_MARKER = b"Return_Data_Over_JE"
_DEFAULT_HOST = "localhost"
_DEFAULT_PORT = 9939
_QUIT_POLL_SECONDS = 0.2
_NEWLINE = b"\n"


class TCPServerHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        """
        接收訊息並嘗試執行指令
        Receive message and try to execute command

        :return: None
        """
        apitestka_logger.info("TCPServerHandler handle")
        # 接收客戶端傳來的資料 / Receive data from client
        command_string = str(self.request.recv(8192).strip(), encoding="utf-8")
        socket = self.request
        apitestka_logger.info(f"command is: {command_string}")

        # 若收到 quit_server 指令，則關閉伺服器 / Shutdown server if quit_server command received
        if command_string == "quit_server":
            self.server.shutdown()
            self.server.close_flag = True
            apitestka_logger.info("Now quit server")
        else:
            try:
                # 嘗試解析 JSON 並執行對應動作 / Try to parse JSON and execute action
                execute_str = json.loads(command_string)
                execute_dict = execute_action(execute_str).items()

                # 將執行結果回傳給客戶端 / Send execution result back to client
                for execute_function, execute_return in execute_dict:
                    socket.sendto(str(execute_return).encode("utf-8"), self.client_address)
                    socket.sendto(_NEWLINE, self.client_address)

                # 傳送結束標記 / Send end marker
                socket.sendto(_END_MARKER, self.client_address)
                socket.sendto(_NEWLINE, self.client_address)
            except Exception as error:
                # 若執行失敗，回傳錯誤訊息 / Send error message if execution fails
                try:
                    socket.sendto(str(error).encode("utf-8"), self.client_address)
                    socket.sendto(_NEWLINE, self.client_address)
                    socket.sendto(_END_MARKER, self.client_address)
                    socket.sendto(_NEWLINE, self.client_address)
                except Exception as inner_error:
                    # 若錯誤處理也失敗，至少回傳結束標記 / If error handling fails, still send end marker
                    apitestka_logger.error(repr(inner_error))
                    socket.sendto(_END_MARKER, self.client_address)
                    socket.sendto(_NEWLINE, self.client_address)


class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    def __init__(self, server_address, request_handler_class):
        """
        初始化 TCP 伺服器
        Initialize TCP server
        """
        apitestka_logger.info("Init TCPServer")
        super().__init__(server_address, request_handler_class)
        self.close_flag: bool = False  # 用來標記伺服器是否關閉 / Flag to indicate server shutdown


def start_apitestka_socket_server(host: str = _DEFAULT_HOST, port: int = _DEFAULT_PORT) -> TCPServer:
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

    # 建立伺服器並啟動執行緒 / Create server and start thread
    server = TCPServer((host, port), TCPServerHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True  # 設定為背景執行緒 / Set as daemon thread
    server_thread.start()

    return server


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
