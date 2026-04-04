===========
Mock Server
===========

APITestka includes a built-in Flask-based mock server for local testing.
It allows easy addition of routes and HTTP methods.

Basic Usage
-----------

.. code-block:: python

   from je_api_testka import flask_mock_server_instance, request

   # Add custom routes
   def my_endpoint():
       return {"message": "hello", "params": dict(request.args)}

   flask_mock_server_instance.add_router(
       {"/api/test": my_endpoint},
       methods=["GET", "POST"]
   )

   # Start the mock server (default: localhost:8090)
   flask_mock_server_instance.start_mock_server()

Route with Method Detection
---------------------------

.. code-block:: python

   from je_api_testka import flask_mock_server_instance, request

   def test_function():
       if request.method == "GET":
           return "GET"
       if request.method == "POST":
           return "POST"

   flask_mock_server_instance.add_router(
       {"/test": test_function},
       methods=["GET", "POST"]
   )
   flask_mock_server_instance.start_mock_server()

Custom Host and Port
--------------------

.. code-block:: python

   from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer

   server = FlaskMockServer("0.0.0.0", 5000)
   server.add_router({"/health": lambda: "OK"}, methods=["GET"])
   server.start_mock_server()
