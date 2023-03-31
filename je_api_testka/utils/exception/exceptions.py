# general

class APITesterException(Exception):
    pass


# get method

class APITesterGetException(APITesterException):
    pass


class APITesterGetDataException(APITesterGetException):
    pass


class APITesterGetJsonException(APITesterGetException):
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


class APITesterXMLTypeException(APITesterXMLException):
    pass


# API data check
class APICheckException(APITesterException):
    pass


class APIStatusCodeException(APICheckException):
    pass


class APITextException(APICheckException):
    pass


class APIContentException(APICheckException):
    pass


class APIHeadersException(APICheckException):
    pass


class APIHistoryException(APICheckException):
    pass


class APIEncodingException(APICheckException):
    pass


class APICookiesException(APICheckException):
    pass


class APIElapsedException(APICheckException):
    pass


class APIRequestsMethodException(APICheckException):
    pass


class APIRequestsUrlException(APICheckException):
    pass


class APIRequestsBodyException(APICheckException):
    pass


# Assert exception

class APIAssertException(APITesterException):
    pass


# html exception

class APIHTMLException(APITesterException):
    pass


# Json

class APIJsonReportException(APITesterException):
    pass


# Executor

class APIAddCommandException(APITesterException):
    pass


# Execute callback
class CallbackExecutorException(APITesterException):
    pass
