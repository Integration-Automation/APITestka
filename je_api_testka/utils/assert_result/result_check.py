from je_api_testka.utils.exception.api_test_exceptions import APIAssertException


def check_result(result_dict: dict, result_check_dict: dict):
    for key, value in result_check_dict.items():
        if result_dict.get(key) != value:
            raise APIAssertException(
                "value should be {right_value} but value was {wrong_value}".format(
                    right_value=value, wrong_value=result_dict.get(key)
                )
            )
