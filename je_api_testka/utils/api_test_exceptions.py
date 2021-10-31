from je_api_testka.utils.api_test_eceptions_tag import api_test_error_message
from je_api_testka.utils.api_test_eceptions_tag import api_test_get_error_message
from je_api_testka.utils.api_test_eceptions_tag import api_test_get_json_error_message
from je_api_testka.utils.api_test_eceptions_tag import api_test_put_error_message
from je_api_testka.utils.api_test_eceptions_tag import api_test_delete_error_message
from je_api_testka.utils.api_test_eceptions_tag import api_test_post_error_message
from je_api_testka.utils.api_test_eceptions_tag import api_test_head_error_message
from je_api_testka.utils.api_test_eceptions_tag import api_test_session_error_message


class APITesterException(Exception):

    def __init__(self, message=api_test_error_message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class APITesterGetDataException(APITesterException):

    def __init__(self, message=api_test_get_error_message):
        super().__init__(message)


class APITesterGetException(APITesterException):

    def __init__(self, message=api_test_get_error_message):
        super().__init__(message)


class APITesterGetJsonException(APITesterException):

    def __init__(self, message=api_test_get_json_error_message):
        super().__init__(message)


class APITesterPutException(APITesterException):

    def __init__(self, message=api_test_put_error_message):
        super().__init__(message)


class APITesterDeleteException(APITesterException):

    def __init__(self, message=api_test_put_error_message):
        super().__init__(message)


class APITesterPostException(APITesterException):

    def __init__(self, message=api_test_post_error_message):
        super().__init__(message)


class APITesterHeadException(APITesterException):

    def __init__(self, message=api_test_head_error_message):
        super().__init__(message)


class APITesterOptionsException(APITesterException):

    def __init__(self, message=api_test_head_error_message):
        super().__init__(message)


class APITesterPatchException(APITesterException):

    def __init__(self, message=api_test_head_error_message):
        super().__init__(message)


class APITesterSessionException(APITesterException):

    def __init__(self, message=api_test_session_error_message):
        super().__init__(message)
