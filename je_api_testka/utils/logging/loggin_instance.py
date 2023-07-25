import logging
import sys

apitestka_logger = logging.getLogger("APITestka")
apitestka_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
# Stream handler
stream_handler = logging.StreamHandler(stream=sys.stderr)
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.WARNING)
apitestka_logger.addHandler(stream_handler)
# File handler
file_handler = logging.FileHandler("APITestka.log")
file_handler.setFormatter(formatter)
apitestka_logger.addHandler(file_handler)

