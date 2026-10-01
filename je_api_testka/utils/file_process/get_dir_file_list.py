from typing import List, Optional

from je_action_core import get_dir_files_as_list as _get_dir_files_as_list

from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def get_dir_files_as_list(dir_path: Optional[str] = None, default_search_file_extension: str = ".json") -> List[str]:
    """
    取得指定目錄下所有符合副檔名的檔案清單
    Get all files in the given directory that end with the specified extension

    :param dir_path: 要搜尋的目錄路徑 (預設為呼叫當下的工作目錄)
                     Directory path to search (default: the current working directory when called)
    :param default_search_file_extension: 要搜尋的副檔名 (預設為 ".json")
                                          File extension to search (default: ".json")
    :return: 若無符合檔案則回傳空清單，否則回傳檔案絕對路徑清單
             [] if no files found, otherwise the absolute paths of the files found
    """
    apitestka_logger.info(
        "get_dir_file_list.py get_dir_files_as_list "
        f"dir_path: {dir_path} "
        f"default_search_file_extension: {default_search_file_extension}"
    )
    return _get_dir_files_as_list(dir_path, default_search_file_extension)
