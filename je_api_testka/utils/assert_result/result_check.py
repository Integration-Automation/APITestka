import sys

from je_api_testka.utils.exception.exceptions import APIAssertException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def check_result(result_dict: dict, result_check_dict: dict) -> None:
    """
    檢查回應資料是否符合預期
    Check if response data matches expected values

    :param result_dict: 回應結果字典 (get_api_response_data 的回傳資料)
                        Response result dictionary (returned from get_api_response_data)
    :param result_check_dict: 包含要檢查的 key 與預期值的字典
                              Dictionary with keys and expected values to validate result_dict
    :return: 無回傳值，若檢查失敗則拋出例外
             No return value, raises exception if validation fails
    """
    apitestka_logger.info(
        f"result_check.py check_result result_dict: {result_dict} result_check_dict: {result_check_dict}"
    )

    # 逐一檢查 result_check_dict 中的 key/value 是否符合 result_dict
    # Iterate through result_check_dict and validate against result_dict
    for key, value in result_check_dict.items():
        if result_dict.get(key) != value:
            # 若不符合，輸出錯誤訊息到 stderr
            # If mismatch, print error message to stderr
            print(
                "value should be {right_value} but value was {wrong_value}".format(
                    right_value=value, wrong_value=result_dict.get(key)
                ),
                file=sys.stderr
            )
            # 並拋出自訂例外 APIAssertException
            # Raise custom exception APIAssertException
            raise APIAssertException(
                "value should be {right_value} but value was {wrong_value}".format(
                    right_value=value, wrong_value=result_dict.get(key)
                )
            )