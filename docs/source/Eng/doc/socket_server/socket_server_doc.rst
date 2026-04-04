=====================================
Remote Automation (Socket Server)
=====================================

APITestka includes a TCP socket server for remote command execution.

Starting the Server
-------------------

.. code-block:: python

   from je_api_testka import start_apitestka_socket_server

   # Start the socket server (default: localhost:9939)
   server = start_apitestka_socket_server(host="localhost", port=9939)

Clients can send JSON-formatted action lists via TCP, and the server will
execute them and return results. Send ``quit_server`` to shut down the server.

CLI Usage
---------

.. code-block:: bash

   python -m je_api_testka.utils.socket_server.api_testka_socket_server localhost 9939
