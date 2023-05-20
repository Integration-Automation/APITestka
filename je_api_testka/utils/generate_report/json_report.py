import json
import sys
import typing
from threading import Lock

from je_api_testka.utils.test_record.test_record_class import test_record_instance
from je_api_testka.utils.exception.exception_tags import cant_save_json_report_record_us_null
from je_api_testka.utils.exception.exceptions import APIJsonReportException


def generate_json() -> typing.Tuple[dict, dict]:
    """
    :return: test success_dict test failure_dict
    """
    if len(test_record_instance.test_record_list) == 0 and len(test_record_instance.error_record_list) == 0:
        raise APIJsonReportException(cant_save_json_report_record_us_null)
    else:
        success_dict = dict()
        success_count: int = 1
        success_test_str: str = "Success_Test"
        for record_data in test_record_instance.test_record_list:
            success_dict.update(
                {
                    success_test_str + str(success_count): {
                        "status_code": str(record_data.get("status_code")),
                        "text": str(record_data.get("text")),
                        "content": str(record_data.get("content"), encoding="utf-8"),
                        "headers": str(record_data.get("headers")),
                        "history": str(record_data.get("history")),
                        "encoding": str(record_data.get("encoding")),
                        "cookies": str(record_data.get("cookies")),
                        "elapsed": str(record_data.get("elapsed")),
                        "request_time_sec": str(record_data.get("request_time_sec")),
                        "request_method": str(record_data.get("request_method")),
                        "request_url": str(record_data.get("request_url")),
                        "request_body": str(record_data.get("request_body")),
                        "start_time": str(record_data.get("start_time")),
                        "end_time": str(record_data.get("end_time")),
                    }
                }
            )
            success_count = success_count + 1
        failure_dict = dict()
        if len(test_record_instance.error_record_list) == 0:
            pass
        else:
            failure_count: int = 1
            failure_test_str: str = "Failure_Test"
            for record_data in test_record_instance.error_record_list:
                failure_dict.update(
                    {
                        failure_test_str: {
                            "http_method": str(record_data[0].get("http_method")),
                            "test_url": str(record_data[0].get("test_url")),
                            "soap": str(record_data[0].get("soap")),
                            "record_request_info": str(record_data[0].get("record_request_info")),
                            "clean_record": str(record_data[0].get("clean_record")),
                            "result_check_dict": str(record_data[0].get("result_check_dict")),
                            "error": str(record_data[1])
                        }
                    }
                )
                failure_count = failure_count + 1
        return success_dict, failure_dict


def generate_json_report(json_file_name: str = "default_name") -> None:
    """
    :param json_file_name: save json file's name
    """
    lock = Lock()
    success_dict, failure_dict = generate_json()
    try:
        lock.acquire()
        with open(json_file_name + "_failure.json", "w+") as file_to_write:
            json.dump(dict(failure_dict), file_to_write, indent=4)
    except Exception as error:
        print(repr(error), file=sys.stderr)
    finally:
        lock.release()
    try:
        lock.acquire()
        with open(json_file_name + "_success.json", "w+") as file_to_write:
            json.dump(dict(success_dict), file_to_write, indent=4)
    except Exception as error:
        print(repr(error), file=sys.stderr)
    finally:
        lock.release()
