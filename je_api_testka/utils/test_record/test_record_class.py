from je_api_testka.utils.logging.loggin_instance import apitestka_logger


class TestRecord(object):
    """
    測試紀錄資料類別，用來保存成功與失敗的測試結果
    Data class to record success and failure test results
    """

    def __init__(self):
        """
        初始化測試紀錄
        Initialize test record
        """
        apitestka_logger.info("Init TestRecord")
        # 成功測試紀錄清單 / List to store successful test records
        self.test_record_list: list = list()
        # 失敗測試紀錄清單 / List to store failed test records
        self.error_record_list: list = list()

    def clean_record(self) -> None:
        """
        清除所有測試紀錄
        Clean all test records
        """
        apitestka_logger.info("TestRecord clean_record")
        self.test_record_list: list = list()
        self.error_record_list: list = list()


# 建立全域測試紀錄實例，供其他模組使用
# Create global test record instance for use across modules
test_record_instance = TestRecord()