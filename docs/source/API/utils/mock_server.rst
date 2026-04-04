===========
Mock Server
===========

FlaskMockServer Class
---------------------

.. code-block:: python

   class FlaskMockServer:

       def __init__(self, host: str, port: int):
           """
           :param host: mock server host name
           :param port: mock server port
           """

       def add_router(self, rule_and_function_dict: dict, **kwargs):
           """
           Add routes to the mock server.

           :param rule_and_function_dict: {"rule_path": function}
           :param kwargs: additional parameters (e.g., methods=["GET", "POST"])
           """

       def start_mock_server(self):
           """Start the mock server."""

Global Instance
---------------

.. code-block:: python

   flask_mock_server_instance = FlaskMockServer("localhost", 8090)

A pre-configured instance available at ``localhost:8090``.
