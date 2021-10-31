from je_api_testka.requests_wrapper.requests_data_structure import api_tester_method

from je_api_testka.utils.api_test_exceptions import APITesterDeleteException
from je_api_testka.utils.api_test_exceptions import APITesterGetDataException
from je_api_testka.utils.get_api_data import get_api_response_data


def test_api_delete(test_url, **kwargs):
    try:
        response = api_tester_method("delete", test_url=test_url, **kwargs)
    except APITesterDeleteException:
        raise APITesterDeleteException
    try:
        response_data = get_api_response_data(response)
    except APITesterGetDataException:
        raise APITesterGetDataException
    return {"response": response, "response_data": response_data}

