from sys import stderr
from typing import Any, Callable, Union

from je_api_testka.requests_wrapper.request_method import test_api_method_requests
from je_api_testka.utils.exception.exception_tags import get_bad_trigger_function, get_bad_trigger_method
from je_api_testka.utils.exception.exceptions import CallbackExecutorException
from je_api_testka.utils.generate_report.html_report_generate import generate_html, generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json, generate_json_report
from je_api_testka.utils.generate_report.xml_report import generate_xml, generate_xml_report
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.mock_server.flask_mock_server import flask_mock_server_instance
from je_api_testka.utils.package_manager.package_manager_class import package_manager


class CallbackFunctionExecutor(object):
    def __init__(self):
        # 初始化 CallbackFunctionExecutor，建立事件字典
        # Initialize CallbackFunctionExecutor and build event dictionary
        apitestka_logger.info("Init CallbackFunctionExecutor")
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

    def callback_function(
            self,
            trigger_function_name: str,
            callback_function: Callable,
            callback_function_param: Union[dict, None] = None,
            callback_param_method: Union[str, None] = "kwargs",
            **kwargs
    ) -> Any:
        """
        執行指定的觸發函式，並在完成後執行回呼函式
        Execute the specified trigger function, then run the callback function

        :param trigger_function_name: 要觸發的函式名稱，只能是 event_dict 中的函式
                                      Name of function to trigger, must exist in event_dict
        :param callback_function: 要執行的回呼函式 / Callback function to execute
        :param callback_function_param: 回呼函式的參數，只接受 dict
                                        Parameters for callback function, only dict accepted
        :param callback_param_method: 回呼函式的參數傳遞方式，只接受 "kwargs" 或 "args"
                                      Parameter passing method for callback, only "kwargs" or "args"
        :param kwargs: 傳給觸發函式的參數 / Parameters passed to trigger function
        :return: 觸發函式的回傳值 / Return value of trigger function
        """
        apitestka_logger.info(
            "CallbackFunctionExecutor callback_function "
            f"trigger_function_name: {trigger_function_name} "
            f"callback_function_param: {callback_function_param} "
            f"callback_param_method: {callback_param_method} "
            f"kwargs: {kwargs}"
        )
        try:
            # 確認觸發函式存在於事件字典 / Ensure trigger function exists in event_dict
            if trigger_function_name not in self.event_dict.keys():
                raise CallbackExecutorException(get_bad_trigger_function)

            # 執行觸發函式 / Execute trigger function
            execute_return_value = self.event_dict.get(trigger_function_name)(**kwargs)

            # 執行回呼函式 / Execute callback function
            if callback_function_param is not None:
                if callback_param_method not in ["kwargs", "args"]:
                    raise CallbackExecutorException(get_bad_trigger_method)
                if callback_param_method == "kwargs":
                    callback_function(**callback_function_param)
                else:
                    callback_function(*callback_function_param)
            else:
                callback_function()

            return execute_return_value
        except Exception as error:
            # 錯誤輸出到 stderr / Print error to stderr
            print(repr(error), file=stderr)


# 建立全域的 callback_executor 並綁定到 package_manager
# Create global callback_executor and bind to package_manager
callback_executor = CallbackFunctionExecutor()
package_manager.executor = callback_executor