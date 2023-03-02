import sys

from je_api_testka.utils.exception.exceptions import APIAssertException


def check_result(result_dict: dict, result_check_dict: dict):
    """
    :param result_dict: response result dict (get_api_response_data's return data)
    :param result_check_dict: the dict include data name and value to check result_dict is valid or not
    :return: True if no error None if check failed
    """
    for key, value in result_check_dict.items():
        if result_dict.get(key) != value:
            print(
                "value should be {right_value} but value was {wrong_value}".format(
                    right_value=value, wrong_value=result_dict.get(key)
                ), file=sys.stderr
            )
            raise APIAssertException("value should be {right_value} but value was {wrong_value}".format(right_value=value,
                                                                                      wrong_value=result_dict.get(key)))
