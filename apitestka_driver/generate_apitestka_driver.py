import sys

from je_api_testka import start_apitestka_socket_server

try:
    server = start_apitestka_socket_server()
    while not server.close_flag:
        pass
    else:
        sys.exit(0)
except Exception as error:
    print(repr(error))
