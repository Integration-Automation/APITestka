import json
import socketserver
import sys
import threading

from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


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
        print("command is: " + command_string, flush=True)

        # 若收到 quit_server 指令，則關閉伺服器 / Shutdown server if quit_server command received
        if command_string == "quit_server":
            self.server.shutdown()
            self.server.close_flag = True
            print("Now quit server", flush=True)
        else:
            try:
                # 嘗試解析 JSON 並執行對應動作 / Try to parse JSON and execute action
                execute_str = json.loads(command_string)
                execute_dict = execute_action(execute_str).items()

                # 將執行結果回傳給客戶端 / Send execution result back to client
                for execute_function, execute_return in execute_dict:
                    socket.sendto(str(execute_return).encode("utf-8"), self.client_address)
                    socket.sendto("\n".encode("utf-8"), self.client_address)

                # 傳送結束標記 / Send end marker
                socket.sendto("Return_Data_Over_JE".encode("utf-8"), self.client_address)
                socket.sendto("\n".encode("utf-8"), self.client_address)
            except Exception as error:
                # 若執行失敗，回傳錯誤訊息 / Send error message if execution fails
                try:
                    socket.sendto(str(error).encode("utf-8"), self.client_address)
                    socket.sendto("\n".encode("utf-8"), self.client_address)
                    socket.sendto("Return_Data_Over_JE".encode("utf-8"), self.client_address)
                    socket.sendto("\n".encode("utf-8"), self.client_address)
                except Exception as error:
                    # 若錯誤處理也失敗，至少回傳結束標記 / If error handling fails, still send end marker
                    print(repr(error))
                    socket.sendto("Return_Data_Over_JE".encode("utf-8"), self.client_address)
                    socket.sendto("\n".encode("utf-8"), self.client_address)


class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    def __init__(self, server_address, request_handler_class):
        """
        初始化 TCP 伺服器
        Initialize TCP server
        """
        apitestka_logger.info("Init TCPServer")
        super().__init__(server_address, request_handler_class)
        self.close_flag: bool = False  # 用來標記伺服器是否關閉 / Flag to indicate server shutdown


def start_apitestka_socket_server(host: str = "localhost", port: int = 9939) -> TCPServer:
    """
    啟動 TCP Socket 伺服器
    Start TCP socket server

    :param host: 伺服器主機 / Server host
    :param port: 伺服器埠號 / Server port
    :return: TCPServer 實例 / TCPServer instance
    """
    apitestka_logger.info(
        f"api_testka_socket_server.py start_apitestka_socket_server host: {host} port: {port}"
    )

    # 支援從命令列參數設定 host 與 port / Support setting host and port from CLI arguments
    if len(sys.argv) == 2:
        host = sys.argv[1]
    elif len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])

    # 建立伺服器並啟動執行緒 / Create server and start thread
    server = TCPServer((host, port), TCPServerHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True  # 設定為背景執行緒 / Set as daemon thread
    server_thread.start()

    return server