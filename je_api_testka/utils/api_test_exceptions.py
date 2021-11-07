class APITesterException(Exception):
    pass


class APITesterGetDataException(APITesterException):
    pass


class APITesterGetException(APITesterException):
    pass


class APITesterGetJsonException(APITesterException):
    pass


class APITesterPutException(APITesterException):
    pass


class APITesterDeleteException(APITesterException):
    pass


class APITesterPostException(APITesterException):
    pass


class APITesterHeadException(APITesterException):
    pass


class APITesterOptionsException(APITesterException):
    pass


class APITesterPatchException(APITesterException):
    pass


class APITesterSessionException(APITesterException):
    pass
