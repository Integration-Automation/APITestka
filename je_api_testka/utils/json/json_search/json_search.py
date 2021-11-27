from json import loads

from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_json_type_error
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_cant_find_element_in_json_error
from je_api_testka.utils.exception.api_test_exceptions import APITesterJsonException


def type_check(check_data):
    if type(check_data) == list:
        return True
    else:
        return False


def json_element_find(search_json: [str, dict], search_key: str, **kwargs):
    if type(search_json) == str:
        search_json = loads(search_json)
    elif type(search_json) == dict or type(search_json) == list:
        pass
    else:
        raise APITesterJsonException(api_test_json_type_error)
    return_data = None
    if iter(search_json) and type_check(search_json):
        return_data = search_json[0].get(search_key)
    else:
        return_data = search_json.get(search_key)
    if return_data is None:
        raise APITesterJsonException(api_test_cant_find_element_in_json_error)
    else:
        return return_data