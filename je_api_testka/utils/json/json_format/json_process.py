import json.decoder
import sys
from json import dumps
from json import loads

from je_api_testka.utils.exception.exception_tags import cant_reformat_json_error
from je_api_testka.utils.exception.exception_tags import wrong_json_data_error
from je_api_testka.utils.exception.exceptions import APITesterJsonException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def __process_json(json_string: str, **kwargs) -> str:
    """
    :param json_string: full json str (not json type)
    :param kwargs: any another kwargs for dumps
    :return: reformat str
    """
    apitestka_logger.info("json_process.py __process_json")
    try:
        return dumps(loads(json_string), indent=4, sort_keys=True, **kwargs)
    except json.JSONDecodeError as error:
        print(wrong_json_data_error, file=sys.stderr)
        raise error
    except TypeError:
        try:
            return dumps(json_string, indent=4, sort_keys=True, **kwargs)
        except TypeError:
            raise APITesterJsonException(wrong_json_data_error)


def reformat_json(json_string: str, **kwargs) -> str:
    """
    :param json_string: valid json string
    :param kwargs: indent, sort_keys or another args
    :return: None
    """
    apitestka_logger.info("json_process.py reformat_json")
    try:
        return __process_json(json_string, **kwargs)
    except APITesterJsonException:
        raise APITesterJsonException(cant_reformat_json_error)
