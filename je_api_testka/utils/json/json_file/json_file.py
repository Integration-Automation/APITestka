"""Action files: je_action_core's JSON reader and writer with APITestka's exception and messages."""
from typing import Any

from je_action_core import ActionJsonFile, JsonFileMessages, JsonFileSettings

from je_api_testka.utils.exception.exception_tags import cant_find_json_error, cant_save_json_error
from je_api_testka.utils.exception.exceptions import APITesterJsonException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

_json_file = ActionJsonFile(JsonFileSettings(
    error=APITesterJsonException,
    messages=JsonFileMessages(missing=f"{cant_find_json_error}: {{path}}",
                              unreadable=f"{cant_find_json_error}: {{path}}: {{error}}",
                              unwritable=f"{cant_save_json_error}: {{path}}: {{error}}"),
    log_info=apitestka_logger.info,
))


def read_action_json(json_file_path: str) -> Any:
    """
    讀取 JSON 檔案並轉換為字典
    Read JSON file and convert to dictionary

    The file is read as UTF-8. A missing file, an unreadable one or invalid JSON raises
    :class:`APITesterJsonException` (the cause is chained), instead of returning ``None`` or
    leaking the underlying error.

    :param json_file_path: JSON 檔案路徑 / Path to JSON file
    :return: JSON 內容 / Parsed JSON content
    """
    return _json_file.read(json_file_path)


def write_action_json(json_save_path: str, action_json: Any) -> None:
    """
    將動作清單寫入 JSON 檔案
    Write action list into JSON file

    The file is written as UTF-8 with non-ASCII text kept as is. A write failure or data that
    cannot be serialised raises :class:`APITesterJsonException` with the cause chained, and data that
    cannot be serialised leaves the file as it was.

    :param json_save_path: JSON 儲存路徑 / Path to save JSON file
    :param action_json: 包含動作的 JSON 結構 / JSON structure containing actions
    """
    _json_file.write(json_save_path, action_json)
