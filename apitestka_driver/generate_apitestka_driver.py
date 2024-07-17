import sys

from je_api_testka import start_apitestka_socket_server

server = start_apitestka_socket_server()
while True:
    if server.close_flag:
        sys.exit(0)
