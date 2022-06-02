class TestRecord(object):
    """
    data class to record success and failure test
    """

    def __init__(self):
        self.test_record_list = list()
        self.error_record_list = list()

    def clean_record(self):
        self.test_record_list = list()
        self.error_record_list = list()


test_record_instance = TestRecord()

