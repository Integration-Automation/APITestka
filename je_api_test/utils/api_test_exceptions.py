from je_api_test.utils.api_test_eceptions_tag import api_test_error_message
from je_api_test.utils.api_test_eceptions_tag import api_test_get_error_message
from je_api_test.utils.api_test_eceptions_tag import api_test_get_json_error_message


class APITesterException(Exception):

    def __init__(self, message=api_test_error_message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class APITesterGetException(AutoControlException):

    def __init__(self, message=api_test_get_error_message):
        super().__init__(message)


class APITesterGetJsonException(AutoControlException):

    def __init__(self, message=api_test_get_json_error_message):
        super().__init__(message)

