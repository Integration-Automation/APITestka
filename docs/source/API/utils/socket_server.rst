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
