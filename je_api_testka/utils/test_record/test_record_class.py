from je_api_testka.utils.logging.loggin_instance import apitestka_logger


class TestRecord(object):
    """
    data class to record success and failure test
    """

    def __init__(self):
        apitestka_logger.info("Init TestRecord")
        self.test_record_list: list = list()
        self.error_record_list: list = list()

    def clean_record(self) -> None:
        apitestka_logger.info("TestRecord clean_record")
        self.test_record_list: list = list()
        self.error_record_list: list = list()


test_record_instance = TestRecord()
