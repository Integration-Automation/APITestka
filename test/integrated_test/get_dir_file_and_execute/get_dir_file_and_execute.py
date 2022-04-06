import os

from je_api_testka import get_dir_files_as_list
from je_api_testka import execute_files

files_list = get_dir_files_as_list(os.getcwd())
if files_list is not None:
    execute_files(files_list)
