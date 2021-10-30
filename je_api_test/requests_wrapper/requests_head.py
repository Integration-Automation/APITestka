from je_api_test.requests_wrapper.requests_data_structure import api_tester_method

from je_api_test.utils.api_test_exceptions import APITesterHeadException
from je_api_test.utils.api_test_exceptions import APITesterGetDataException
from je_api_test.utils.get_api_data import get_api_response_data


def test_api_head(test_url, **kwargs):
    try:
        response = api_tester_method("head", test_url=test_url, **kwargs)
    except APITesterHeadException:
        raise APITesterHeadException
    try:
        response_data = get_api_response_data(response)
    except APITesterGetDataException:
        raise APITesterGetDataException
    return {"response": response, "response_data": response_data}

