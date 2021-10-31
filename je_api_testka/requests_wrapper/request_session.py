from requests import Session

from je_api_testka.utils.api_test_exceptions import APITesterSessionException
from je_api_testka.utils.api_test_exceptions import APITesterGetDataException
from je_api_testka.utils.get_api_data import get_api_response_data


def test_api_session(test_url, **kwargs):
    try:
        response = Session().get(test_url, **kwargs)
    except APITesterSessionException:
        raise APITesterSessionException
    try:
        response_data = get_api_response_data(response)
    except APITesterGetDataException:
        raise APITesterGetDataException

    return {"response": response, "response_data": response_data}

