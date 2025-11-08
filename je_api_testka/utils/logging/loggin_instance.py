import logging
from logging.handlers import RotatingFileHandler

from je_api_testka.gui.message_queue import api_testka_ui_queue

logging.root.setLevel(logging.DEBUG)
apitestka_logger = logging.getLogger("APITestka")
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')


class APITestkaLoggingHandler(RotatingFileHandler):

    # redirect logging stderr output to queue

    def __init__(self, filename: str = "APITestka.log", mode="w",
                 max_bytes:int=1073741824, backup_count:int=0):
        super().__init__(filename=filename, mode=mode, maxBytes=max_bytes, backupCount=backup_count)
        self.formatter = formatter
        self.setLevel(logging.DEBUG)

    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)

class QueueLogHandler(logging.Handler):
    """
    自訂 Logger Handler，把訊息丟到 UI 佇列
    Custom logger handler that pushes log records into UI queue
    """

    def emit(self, record: logging.LogRecord):
        log_entry = self.format(record)
        api_testka_ui_queue.put(log_entry)

# File handler
file_handler = APITestkaLoggingHandler()
file_handler.setFormatter(formatter)
queue_log_handler = QueueLogHandler()
apitestka_logger.addHandler(queue_log_handler)
apitestka_logger.addHandler(file_handler)
