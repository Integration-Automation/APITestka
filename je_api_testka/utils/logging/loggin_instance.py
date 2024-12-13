import logging

logging.root.setLevel(logging.DEBUG)
apitestka_logger = logging.getLogger("APITestka")
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
# File handler
file_handler = logging.FileHandler(filename="APITestka.log", mode="w")
file_handler.setFormatter(formatter)
apitestka_logger.addHandler(file_handler)

class APITestkaLoggingHandler(logging.Handler):

    # redirect logging stderr output to queue

    def __init__(self):
        super().__init__()
        self.formatter = formatter
        self.setLevel(logging.DEBUG)

    def emit(self, record: logging.LogRecord) -> None:
        print(self.format(record))


# Stream handler
apitestka_logger.addHandler(APITestkaLoggingHandler())
