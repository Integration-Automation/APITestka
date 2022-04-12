from pathlib import Path


def create_dir(dir_name: str):
    Path(dir_name).mkdir(
        parents=True,
        exist_ok=True
    )


def create_template_dir():
    create_dir("api_testka/template")
