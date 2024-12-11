from os import getcwd
from os import walk
from os.path import abspath
from os.path import join
from typing import List

from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def get_dir_files_as_list(dir_path: str = getcwd(), default_search_file_extension: str = ".json") -> List:
    """
    get dir file when end with default_search_file_extension
    :param dir_path: which dir we want to walk and get file list
    :param default_search_file_extension: which extension we want to search
    :return: [] if nothing searched or [file1, file2.... files] file was searched
    """
    apitestka_logger.info("get_dir_file_list.py get_dir_files_as_list "
                          f"dir_path: {dir_path} "
                          f"default_search_file_extension: {default_search_file_extension}")
    return [
        abspath(join(dir_path, file)) for root, dirs, files in walk(dir_path)
        for file in files
        if file.endswith(default_search_file_extension.lower())
    ]
