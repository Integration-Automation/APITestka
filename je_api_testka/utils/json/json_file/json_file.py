import json
from pathlib import Path
from threading import Lock
from typing import Dict

from je_api_testka.utils.exception.exception_tags import cant_find_json_error
from je_api_testka.utils.exception.exception_tags import cant_save_json_error
from je_api_testka.utils.exception.exceptions import APITesterJsonException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

# 使用 Lock 確保多執行緒存取檔案時的安全
# Use Lock to ensure thread-safe file access
lock = Lock()


def read_action_json(json_file_path: str) -> Dict:
    """
    讀取 JSON 檔案並轉換為字典
    Read JSON file and convert to dictionary

    :param json_file_path: JSON 檔案路徑 / Path to JSON file
    :return: JSON 內容轉換成的字典 / Dictionary parsed from JSON
    """
    apitestka_logger.info("json_file.py read_action_json")
    try:
        lock.acquire()  # 確保多執行緒安全 / Ensure thread safety
        file_path = Path(json_file_path)
        if file_path.exists() and file_path.is_file():
            with open(json_file_path) as read_file:
                return json.load(read_file)
    except APITesterJsonException:
        # 若讀取失敗，拋出自訂例外
        # Raise custom exception if reading fails
        raise APITesterJsonException(cant_find_json_error)
    finally:
        lock.release()


def write_action_json(json_save_path: str, action_json: list) -> None:
    """
    將動作清單寫入 JSON 檔案
    Write action list into JSON file

    :param json_save_path: JSON 儲存路徑 / Path to save JSON file
    :param action_json: 包含動作的 JSON 結構 (list) / JSON structure (list) containing actions
    """
    apitestka_logger.info("json_file.py write_action_json")
    try:
        lock.acquire()  # 確保多執行緒安全 / Ensure thread safety
        with open(json_save_path, "w+") as file_to_write:
            file_to_write.write(json.dumps(action_json, indent=4))
    except APITesterJsonException:
        # 若寫入失敗，拋出自訂例外
        # Raise custom exception if writing fails
        raise APITesterJsonException(cant_save_json_error)
    finally:
        lock.release()