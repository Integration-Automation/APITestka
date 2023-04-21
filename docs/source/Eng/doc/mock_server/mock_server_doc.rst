Mock Server
----

* Mock Server is used to simulate a server environment for testing APITestka scripts.
* Mock Server allows for easy addition of routes and methods.

.. code-block:: python

    from je_api_testka import flask_mock_server_instance, request

    # The triggered method can be determined by request.method to identify the type of request
    def test_function():
        if request.method == "GET":
            return "GET"
        if request.method == "POST":
            return "POST"

    # Setting a router rule (path) with the associated function to be triggered and the accepted HTTP methods.
    flask_mock_server_instance.add_router({"/test": test_function}, methods=["GET", "POST"])
    # Start running the Mock Server.
    flask_mock_server_instance.start_mock_server()
