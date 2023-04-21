import typing

from flask.app import Flask

from je_api_testka.utils.exception.exception_tags import get_bad_api_router_setting
from je_api_testka.utils.exception.exceptions import MockServerException


class FlaskMockServer(object):
    pass

    def __init__(self, host, port):
        self.app = Flask(__name__)
        self.host = host
        self.port = port

    
    def api_testka_index_function(self):
        return "APITestka main index"

    def add_router(self, rule_and_function_dict: dict, **kwargs):
        for rule, function in rule_and_function_dict.items():
            if isinstance(rule, str) and isinstance(function, typing.Callable):
                self.app.route(rule, **kwargs)(function)
            else:
                raise MockServerException(get_bad_api_router_setting)

    def start_mock_server(self):
        self.add_router(
            {"/": self.api_testka_index_function},
            methods=["GET"]
        )
        self.app.run(self.host, self.port)


flask_mock_server_instance = FlaskMockServer("localhost", 8090)
