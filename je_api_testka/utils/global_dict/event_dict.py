from je_api_testka.utils.executor.action_executor import execute_action, execute_files

from je_api_testka.requests_wrapper.request_method import test_api_method
from je_api_testka.utils.generate_report.html_report_generate import generate_html
from je_api_testka.utils.generate_report.html_report_generate import generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json
from je_api_testka.utils.generate_report.json_report import generate_json_report
from je_api_testka.utils.generate_report.xml_report import generate_xml
from je_api_testka.utils.generate_report.xml_report import generate_xml_report
from je_api_testka.utils.mock_server.flask_mock_server import flask_mock_server_instance
from je_api_testka.utils.package_manager.package_manager_class import package_manager

event_dict = {
    # test api
    "test_api_method": test_api_method,
    "generate_html": generate_html,
    "generate_html_report": generate_html_report,
    "generate_json": generate_json,
    "generate_json_report": generate_json_report,
    "generate_xml": generate_xml,
    "generate_xml_report": generate_xml_report,
    # execute
    "execute_action": execute_action,
    "execute_files": execute_files,
    "add_package_to_executor": package_manager.add_package_to_executor,
    # mock
    "flask_mock_server_add_router": flask_mock_server_instance.add_router,
    "start_flask_mock_server": flask_mock_server_instance.start_mock_server,
}
