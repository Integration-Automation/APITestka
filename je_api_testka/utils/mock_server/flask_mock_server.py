import typing

from flask.app import Flask


class FlaskMockServer(object):
    pass

    def __init__(self, host, port):
        self.app = Flask(__name__)
        self.host = host
        self.port = port

    
    def api_testka_index_function(self):
        return "APITestka main index"

    def add_router(self, rule_and_function_dict: dict):
        for rule, function in rule_and_function_dict.items():
            if isinstance(rule, str) and isinstance(function, typing.Callable):
                self.app.route(rule)(function)
            else:
                pass

    def start_mock_server(self):
        self.add_router({"/": self.api_testka_index_function()})
        self.app.run(self.host, self.port)


def test():
    return "Test"


mock = FlaskMockServer("localhost", 8080)
mock.add_router({"/test": test})
mock.start_mock_server()
