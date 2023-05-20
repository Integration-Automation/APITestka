class TestRecord(object):
    """
    data class to record success and failure test
    """

    def __init__(self):
        self.test_record_list: list = list()
        self.error_record_list: list = list()

    def clean_record(self) -> None:
        self.test_record_list: list = list()
        self.error_record_list: list = list()


test_record_instance = TestRecord()
