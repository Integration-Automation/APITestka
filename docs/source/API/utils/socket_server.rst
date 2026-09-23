=============
Socket Server
=============

.. code-block:: python

   def start_apitestka_socket_server(
       host: str = "localhost",
       port: int = 9939
   ):

Start a TCP socket server for remote command execution.

:param host: server host (default: ``"localhost"``)
:param port: server port (default: ``9939``)
:return: TCPServer instance

The server accepts JSON-formatted action lists via TCP and executes them.
Send ``"quit_server"`` to shut down.

The function binds exactly the ``host`` and ``port`` it is given. To run the
server from a shell, use the module's command line, which takes an optional
host and port and blocks until a client sends ``quit_server``:

.. code-block:: bash

   python -m je_api_testka.utils.socket_server.api_testka_socket_server [host [port]]
