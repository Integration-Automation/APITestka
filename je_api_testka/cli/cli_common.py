"""Helpers shared by the ``apitestka`` subcommands."""
from __future__ import annotations

from pathlib import Path

from je_api_testka.utils.executor.action_executor import execute_action, execute_files
from je_api_testka.utils.file_process.get_dir_file_list import get_dir_files_as_list
from je_api_testka.utils.json.json_file.json_file import read_action_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

EXIT_OK: int = 0
EXIT_FAILED: int = 1
EXIT_USAGE: int = 2


def run_action_path(target: Path) -> int:
    """Execute an action JSON file, or every JSON file in a directory; return 2 when ``target`` is missing."""
    if target.is_dir():
        execute_files(get_dir_files_as_list(str(target)))
    elif target.is_file():
        execute_action(read_action_json(str(target)))
    else:
        apitestka_logger.error(f"cli: path not found: {target}")
        return EXIT_USAGE
    return EXIT_OK
