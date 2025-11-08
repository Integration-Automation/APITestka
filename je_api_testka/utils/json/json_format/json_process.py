import json.decoder
import sys
from json import dumps, loads

from je_api_testka.utils.exception.exception_tags import cant_reformat_json_error, wrong_json_data_error
from je_api_testka.utils.exception.exceptions import APITesterJsonException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def __process_json(json_string: str, **kwargs) -> str:
    """
    將 JSON 字串重新格式化（縮排、排序）
    Reformat JSON string (indentation, sorting)

    :param json_string: 完整的 JSON 字串 (非 dict 型態)
                        Full JSON string (not dict type)
    :param kwargs: 傳遞給 dumps 的其他參數
                   Additional kwargs for dumps
    :return: 格式化後的 JSON 字串 / Reformatted JSON string
    """
    apitestka_logger.info("json_process.py __process_json")
    try:
        # 嘗試將字串解析為 JSON，再重新格式化
        # Try to parse string into JSON, then reformat
        return dumps(loads(json_string), indent=4, sort_keys=True, **kwargs)
    except json.JSONDecodeError as error:
        # 若解析失敗，輸出錯誤訊息並拋出例外
        # If parsing fails, print error message and raise exception
        print(wrong_json_data_error, file=sys.stderr)
        raise error
    except TypeError:
        # 若傳入的不是字串，直接嘗試格式化
        # If input is not a string, try formatting directly
        try:
            return dumps(json_string, indent=4, sort_keys=True, **kwargs)
        except TypeError:
            # 若仍失敗，拋出自訂例外
            # If still fails, raise custom exception
            raise APITesterJsonException(wrong_json_data_error)


def reformat_json(json_string: str, **kwargs) -> str:
    """
    對外提供的 JSON 格式化函式
    Public function to reformat JSON string

    :param json_string: 合法的 JSON 字串 / Valid JSON string
    :param kwargs: 可選參數，例如 indent、sort_keys
                   Optional args such as indent, sort_keys
    :return: 格式化後的 JSON 字串 / Reformatted JSON string
    """
    apitestka_logger.info("json_process.py reformat_json")
    try:
        return __process_json(json_string, **kwargs)
    except APITesterJsonException:
        # 若格式化失敗，拋出自訂例外
        # Raise custom exception if reformatting fails
        raise APITesterJsonException(cant_reformat_json_error)