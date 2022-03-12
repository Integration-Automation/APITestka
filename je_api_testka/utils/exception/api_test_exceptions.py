# general


class APITesterException(Exception):
    pass


# get method


class APITesterGetDataException(APITesterException):
    pass


class APITesterGetException(APITesterException):
    pass


class APITesterGetJsonException(APITesterException):
    pass


# put method


class APITesterPutException(APITesterException):
    pass


# delete method


class APITesterDeleteException(APITesterException):
    pass


# put method


class APITesterPostException(APITesterException):
    pass


# head method


class APITesterHeadException(APITesterException):
    pass


# options method


class APITesterOptionsException(APITesterException):
    pass


# patch method


class APITesterPatchException(APITesterException):
    pass


# session method


class APITesterSessionException(APITesterException):
    pass


# execute


class APITesterExecuteException(APITesterException):
    pass


# json


class APITesterJsonException(APITesterException):
    pass


# xml


class APITesterXMLException(APITesterException):
    pass


class APITesterXMLTypeException(APITesterException):
    pass


# API data check


class APIStatusCodeException(APITesterException):
    pass


class APITextException(APITesterException):
    pass


class APIContentException(APITesterException):
    pass


class APIHeadersException(APITesterException):
    pass


class APIHistoryException(APITesterException):
    pass


class APIEncodingException(APITesterException):
    pass


class APICookiesException(APITesterException):
    pass


class APIElapsedException(APITesterException):
    pass


class APIRequestsMethodException(APITesterException):
    pass


class APIRequestsUrlException(APITesterException):
    pass


class APIRequestsBodyException(APITesterException):
    pass


# check exception

class APIAssertException(APITesterException):
    pass
