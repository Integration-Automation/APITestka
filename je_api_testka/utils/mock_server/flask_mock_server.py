from flask.app import Flask

from je_api_testka.utils.exception.exception_tags import get_bad_api_router_setting
from je_api_testka.utils.exception.exceptions import MockServerException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.mock_server.dynamic_router import DynamicRouter
from je_api_testka.utils.mock_server.fault_injection import FaultInjector
from je_api_testka.utils.mock_server.openapi_loader import register_openapi_routes
from je_api_testka.utils.mock_server.stateful_store import StatefulStore


class FlaskMockServer:

    def __init__(self, host, port):
        """
        初始化模擬伺服器
        Initialize mock server

        :param host: 模擬伺服器的主機名稱 / Mock server host name
        :param port: 模擬伺服器的埠號 / Mock server port
        """
        apitestka_logger.info("Init FlaskMockServer")
        # Mock server intended for local API testing only; no form auth surface,
        # no CSRF token mechanism is applicable. Not for production use.
        self.app = Flask(__name__)  # NOSONAR S4502
        self.host = host
        self.port = port
        self.state = StatefulStore()
        self.fault_injector = FaultInjector()
        self.dynamic_router = DynamicRouter()

    @classmethod
    def api_testka_index_function(cls) -> str:
        """
        預設首頁路由函式
        Default index route function
        """
        apitestka_logger.info("FlaskMockServer api_testka_index_function")
        return "APITestka main index"

    def add_dynamic_route(self, rule: str, methods=None) -> None:
        """Register a single endpoint backed by the configured DynamicRouter."""
        apitestka_logger.info(f"FlaskMockServer add_dynamic_route rule: {rule}")
        view = self.fault_injector.wrap(self.dynamic_router.dispatch)
        view.__name__ = f"dynamic_{rule.strip('/').replace('/', '_') or 'root'}"
        self.app.route(rule, methods=methods or ["GET"])(view)

    def load_openapi(self, spec: dict) -> dict:
        """Mass-register endpoints from an OpenAPI 3.x document."""
        apitestka_logger.info("FlaskMockServer load_openapi")
        return register_openapi_routes(self, spec)

    def add_router(self, rule_and_function_dict: dict, **kwargs) -> None:
        """
        新增路由到 Flask 應用程式
        Add routes to Flask application

        :param rule_and_function_dict: 字典格式 {"路徑(path)": 對應函式}
                                       Dictionary {"path": function}
        :param kwargs: 可選參數，例如 methods=["GET", "POST"]
                       Optional parameters, e.g., methods=["GET", "POST"]
        """
        apitestka_logger.info(
            "FlaskMockServer add_router "
            f"rule_and_function_dict: {rule_and_function_dict} kwargs: {kwargs}"
        )
        for rule, function in rule_and_function_dict.items():
            if isinstance(rule, str) and callable(function):
                # 將路由與函式綁定到 Flask 應用程式
                # Bind route and function to Flask application
                self.app.route(rule, **kwargs)(function)
            else:
                # 若路由或函式型態錯誤，拋出自訂例外
                # Raise custom exception if route or function type is invalid
                apitestka_logger.error(
                    f"add_router, rule_and_function_dict: {rule_and_function_dict}, params: {kwargs}, "
                    f"failed: {MockServerException(get_bad_api_router_setting)}"
                )
                raise MockServerException(get_bad_api_router_setting)

    def start_mock_server(self) -> None:
        """
        啟動模擬伺服器
        Start mock server
        """
        apitestka_logger.info("FlaskMockServer start_mock_server")
        # 預設加入首頁路由 / Add default index route
        self.add_router(
            {"/": self.api_testka_index_function},
            methods=["GET"]
        )
        # 啟動 Flask 應用程式 / Run Flask application
        self.app.run(self.host, self.port)


# 建立全域模擬伺服器實例，預設 host=localhost, port=8090
# Create global mock server instance, default host=localhost, port=8090
flask_mock_server_instance = FlaskMockServer("localhost", 8090)