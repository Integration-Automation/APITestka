from os import getcwd, walk
from os.path import abspath, join
from typing import List

from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def get_dir_files_as_list(dir_path: str = getcwd(), default_search_file_extension: str = ".json") -> List:
    """
    取得指定目錄下所有符合副檔名的檔案清單
    Get all files in the given directory that end with the specified extension

    :param dir_path: 要搜尋的目錄路徑 (預設為目前工作目錄)
                     Directory path to search (default: current working directory)
    :param default_search_file_extension: 要搜尋的副檔名 (預設為 ".json")
                                          File extension to search (default: ".json")
    :return: 若無符合檔案則回傳空清單，否則回傳檔案路徑清單
             [] if no files found, otherwise [file1, file2, ...] list of file paths
    """
    apitestka_logger.info(
        "get_dir_file_list.py get_dir_files_as_list "
        f"dir_path: {dir_path} "
        f"default_search_file_extension: {default_search_file_extension}"
    )

    # 使用 os.walk 遍歷目錄，取得所有符合副檔名的檔案
    # Use os.walk to traverse directory and collect files with matching extension
    return [
        abspath(join(dir_path, file))  # 轉換為絕對路徑 / Convert to absolute path
        for root, dirs, files in walk(dir_path)  # 遍歷目錄 / Traverse directory
        for file in files
        if file.endswith(default_search_file_extension.lower())  # 檢查副檔名 / Check file extension
    ]