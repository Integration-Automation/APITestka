from flask import request

from je_api_testka import flask_mock_server_instance


def test_function():
    if request.method == "GET":
        return "GET"
    if request.method == "POST":
        return "POST"


flask_mock_server_instance.add_router({"/test": test_function}, methods=["GET", "POST"])
flask_mock_server_instance.start_mock_server()
