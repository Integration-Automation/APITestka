import json
import socketserver
import sys
import threading

from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


class TCPServerHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        """
        Receive message and try to execute message
        :return: None
        """
        apitestka_logger.info("TCPServerHandler handle")
        command_string = str(self.request.recv(8192).strip(), encoding="utf-8")
        socket = self.request
        print("command is: " + command_string, flush=True)
        if command_string == "quit_server":
            self.server.shutdown()
            self.server.close_flag = True
            print("Now quit server", flush=True)
        else:
            try:
                execute_str = json.loads(command_string)
                execute_dict = execute_action(execute_str).items()
                for execute_function, execute_return in execute_dict:
                    socket.sendto(str(execute_return).encode("utf-8"), self.client_address)
                    socket.sendto("\n".encode("utf-8"), self.client_address)
                socket.sendto("Return_Data_Over_JE".encode("utf-8"), self.client_address)
                socket.sendto("\n".encode("utf-8"), self.client_address)
            except Exception as error:
                try:
                    socket.sendto(str(error).encode("utf-8"), self.client_address)
                    socket.sendto("\n".encode("utf-8"), self.client_address)
                    socket.sendto("Return_Data_Over_JE".encode("utf-8"), self.client_address)
                    socket.sendto("\n".encode("utf-8"), self.client_address)
                except Exception as error:
                    print(repr(error))
                    socket.sendto("Return_Data_Over_JE".encode("utf-8"), self.client_address)
                    socket.sendto("\n".encode("utf-8"), self.client_address)


class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    def __init__(self, server_address, request_handler_class):
        apitestka_logger.info("Init TCPServer")
        super().__init__(server_address, request_handler_class)
        self.close_flag: bool = False


def start_apitestka_socket_server(host: str = "localhost", port: int = 9939) -> TCPServer:
    """
    Start TCP socket server on host with port
    :param host: Server host.
    :param port: Server port.
    :return: TCP server instance.
    """
    apitestka_logger.info("api_testka_socket_server.py start_apitestka_socket_server "
                          f"host: {host} "
                          f"port: {port}")
    if len(sys.argv) == 2:
        host = sys.argv[1]
    elif len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
    server = TCPServer((host, port), TCPServerHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return server
