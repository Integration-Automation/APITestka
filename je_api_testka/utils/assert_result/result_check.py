import sys

from je_api_testka.utils.exception.exceptions import APIAssertException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def check_result(result_dict: dict, result_check_dict: dict) -> None:
    """
    :param result_dict: response result dict (get_api_response_data's return data)
    :param result_check_dict: the dict include data name and value to check result_dict is valid or not
    :return: True if no error None if check failed
    """
    apitestka_logger.info(f"result_check.py check_result "
                          f"result_dict: {result_dict} "
                          f"result_check_dict: {result_check_dict}"
                          )
    for key, value in result_check_dict.items():
        if result_dict.get(key) != value:
            print(
                "value should be {right_value} but value was {wrong_value}".format(
                    right_value=value, wrong_value=result_dict.get(key)
                ), file=sys.stderr
            )
            raise APIAssertException(
                "value should be {right_value} but value was {wrong_value}".format(
                    right_value=value, wrong_value=result_dict.get(key)))
