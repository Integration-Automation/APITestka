from je_action_core import CallbackErrorPolicy, CallbackSettings, CommandRegistry
from je_action_core import CallbackFunctionExecutor as _CoreCallbackExecutor

from je_api_testka.requests_wrapper.request_method import test_api_method_requests
from je_api_testka.utils.exception.exception_tags import (
    get_bad_trigger_function,
    get_bad_trigger_method,
)
from je_api_testka.utils.exception.exceptions import CallbackExecutorException
from je_api_testka.utils.generate_report.html_report_generate import (
    generate_html,
    generate_html_report,
)
from je_api_testka.utils.generate_report.json_report import (
    generate_json,
    generate_json_report,
)
from je_api_testka.utils.generate_report.xml_report import (
    generate_xml,
    generate_xml_report,
)
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.mock_server.flask_mock_server import flask_mock_server_instance
from je_api_testka.utils.package_manager.package_manager_class import package_manager

_SETTINGS = CallbackSettings(
    error=CallbackExecutorException,
    unknown_trigger_message=get_bad_trigger_function,
    bad_method_message=get_bad_trigger_method,
    on_error=CallbackErrorPolicy.RETURN_NONE,  # a failed trigger or callback is logged and returns None
    log_info=apitestka_logger.info,
    log_error=apitestka_logger.error,
)


class CallbackFunctionExecutor(_CoreCallbackExecutor):
    """Runs an ``AT_*`` trigger, then a callback (je_action_core's callback executor with APITestka's settings)."""

    def __init__(self) -> None:
        super().__init__(CommandRegistry(), _SETTINGS)
        # 初始化 CallbackFunctionExecutor，建立事件字典
        # Initialize CallbackFunctionExecutor and build event dictionary
        self.event_dict = {
            # 測試 API / Test API
            "AT_test_api_method": test_api_method_requests,
            # 報告生成 / Report generation
            "AT_generate_html": generate_html,
            "AT_generate_html_report": generate_html_report,
            "AT_generate_json": generate_json,
            "AT_generate_json_report": generate_json_report,
            "AT_generate_xml": generate_xml,
            "AT_generate_xml_report": generate_xml_report,
            # 模擬伺服器 / Mock server
            "AT_flask_mock_server_add_router": flask_mock_server_instance.add_router,
            "AT_start_flask_mock_server": flask_mock_server_instance.start_mock_server,
            # 套件管理 / Package manager
            "AT_add_package_to_callback_executor": package_manager.add_package_to_callback_executor,
        }


# 建立全域的 callback_executor 並綁定到 package_manager
# Create global callback_executor and bind to package_manager
callback_executor = CallbackFunctionExecutor()
package_manager.callback_executor = callback_executor
