import json.decoder
import sys
from json import dumps
from json import loads

from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_cant_reformat_json_error
from je_api_testka.utils.exception.api_test_eceptions_tag import wrong_json_data_error
from je_api_testka.utils.exception.api_test_exceptions import APITesterJsonException


def __process_json(json_string: str, **kwargs):
    try:
        return dumps(loads(json_string), indent=4, sort_keys=True, **kwargs)
    except json.JSONDecodeError as error:
        print(wrong_json_data_error, file=sys.stderr)
        raise error

    except TypeError:
        return dumps(json_string, indent=4, sort_keys=True, **kwargs)


def reformat_json(json_string: str, **kwargs):
    try:
        return __process_json(json_string, **kwargs)
    except APITesterJsonException:
        raise APITesterJsonException(api_test_cant_reformat_json_error)


if __name__ == "__main__":
    test_json_string = '[["get", "http://httpbin.org/get", false, {"headers": {"x-requested-with": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded", "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"}}], ["post", "http://httpbin.org/post", false, {"params": {"task": "new task"}}]]'
    print(reformat_json(test_json_string))
