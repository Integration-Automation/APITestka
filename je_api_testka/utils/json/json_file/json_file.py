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

    The file is read as UTF-8. A missing file, an unreadable one or invalid JSON raises
    :class:`APITesterJsonException` (the cause is chained), instead of returning ``None`` or
    leaking the underlying error.

    :param json_file_path: JSON 檔案路徑 / Path to JSON file
    :return: JSON 內容轉換成的字典 / Dictionary parsed from JSON
    """
    apitestka_logger.info("json_file.py read_action_json")
    file_path = Path(json_file_path)
    if not file_path.is_file():
        raise APITesterJsonException(f"{cant_find_json_error}: {json_file_path}")
    with lock:  # 確保多執行緒安全 / Ensure thread safety
        try:
            with open(file_path, encoding="utf-8") as read_file:
                return json.load(read_file)
        except (OSError, ValueError) as error:
            raise APITesterJsonException(f"{cant_find_json_error}: {json_file_path}: {error}") from error


def write_action_json(json_save_path: str, action_json: list) -> None:
    """
    將動作清單寫入 JSON 檔案
    Write action list into JSON file

    The file is written as UTF-8 with non-ASCII text kept as is. A write failure or data that
    cannot be serialised raises :class:`APITesterJsonException` with the cause chained.

    :param json_save_path: JSON 儲存路徑 / Path to save JSON file
    :param action_json: 包含動作的 JSON 結構 (list) / JSON structure (list) containing actions
    """
    apitestka_logger.info("json_file.py write_action_json")
    with lock:  # 確保多執行緒安全 / Ensure thread safety
        try:
            content = json.dumps(action_json, indent=4, ensure_ascii=False)
            with open(json_save_path, "w", encoding="utf-8") as file_to_write:
                file_to_write.write(content)
        except (OSError, TypeError, ValueError) as error:
            raise APITesterJsonException(f"{cant_save_json_error}: {json_save_path}: {error}") from error
