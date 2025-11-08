from os import getcwd
from pathlib import Path
from threading import Lock

from je_api_testka.utils.json.json_file.json_file import write_action_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.project.template.template_executor import (
    executor_template_1,
    executor_template_2,
    bad_executor_template_1,
)
from je_api_testka.utils.project.template.template_keyword import (
    template_keyword_1,
    template_keyword_2,
    bad_template_1,
)


def create_dir(dir_name: str) -> None:
    """
    建立資料夾
    Create directory

    :param dir_name: 要建立的資料夾名稱 / Directory name to create
    :return: None
    """
    apitestka_logger.info(f"create_project_structure.py create_dir dir_name: {dir_name}")
    Path(dir_name).mkdir(
        parents=True,   # 若父層不存在則一併建立 / Create parent directories if not exist
        exist_ok=True   # 若已存在則不拋出錯誤 / Do not raise error if directory exists
    )


def create_template(parent_name: str, project_path: str = None) -> None:
    """
    在指定目錄下建立範本檔案
    Create template files under the given directory

    :param parent_name: 專案資料夾名稱 / Project folder name
    :param project_path: 專案路徑，若為 None 則使用當前工作目錄 / Project path, default is current working directory
    :return: None
    """
    apitestka_logger.info(
        "create_project_structure.py create_template "
        f"parent_name: {parent_name} project_path: {project_path}"
    )
    if project_path is None:
        project_path = getcwd()

    keyword_dir_path = Path(project_path + "/" + parent_name + "/keyword")
    executor_dir_path = Path(project_path + "/" + parent_name + "/executor")
    lock = Lock()

    # 建立 keyword 範本 JSON 檔案 / Create keyword template JSON files
    if keyword_dir_path.exists() and keyword_dir_path.is_dir():
        write_action_json(project_path + "/" + parent_name + "/keyword/keyword1.json", template_keyword_1)
        write_action_json(project_path + "/" + parent_name + "/keyword/keyword2.json", template_keyword_2)
        write_action_json(project_path + "/" + parent_name + "/keyword/bad_keyword_1.json", bad_template_1)

    # 建立 executor 範本 Python 檔案 / Create executor template Python files
    if executor_dir_path.exists() and keyword_dir_path.is_dir():
        lock.acquire()
        try:
            with open(project_path + "/" + parent_name + "/executor/executor_one_file.py", "w+") as file:
                file.write(
                    executor_template_1.replace(
                        "{temp}",
                        project_path + "/" + parent_name + "/keyword/keyword1.json"
                    )
                )
            with open(project_path + "/" + parent_name + "/executor/executor_bad_file.py", "w+") as file:
                file.write(
                    bad_executor_template_1.replace(
                        "{temp}",
                        project_path + "/" + parent_name + "/keyword/bad_keyword_1.json"
                    )
                )
            with open(project_path + "/" + parent_name + "/executor/executor_folder.py", "w+") as file:
                file.write(
                    executor_template_2.replace(
                        "{temp}",
                        project_path + "/" + parent_name + "/keyword"
                    )
                )
        finally:
            lock.release()


def create_project_dir(project_path: str = None, parent_name: str = "APITestka") -> None:
    """
    建立專案資料夾結構並生成範本
    Create project directory structure and generate templates

    :param project_path: 專案路徑，若為 None 則使用當前工作目錄 / Project path, default is current working directory
    :param parent_name: 專案資料夾名稱 / Project folder name
    :return: None
    """
    apitestka_logger.info(
        "create_project_structure.py create_project_dir "
        f"project_path: {project_path} parent_name: {parent_name}"
    )
    if project_path is None:
        project_path = getcwd()

    # 建立 keyword 與 executor 資料夾 / Create keyword and executor directories
    create_dir(project_path + "/" + parent_name + "/keyword")
    create_dir(project_path + "/" + parent_name + "/executor")

    # 建立範本檔案 / Generate template files
    create_template(parent_name)