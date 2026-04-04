import os

from je_api_testka import create_project_dir


def test_create_project_dir(tmp_path):
    """Create project directory structure and verify files exist."""
    project_path = str(tmp_path)
    create_project_dir(project_path=project_path, parent_name="TestProject")

    keyword_dir = os.path.join(project_path, "TestProject", "keyword")
    executor_dir = os.path.join(project_path, "TestProject", "executor")

    assert os.path.isdir(keyword_dir)
    assert os.path.isdir(executor_dir)

    # Verify keyword template files were created
    assert os.path.exists(os.path.join(keyword_dir, "keyword1.json"))
    assert os.path.exists(os.path.join(keyword_dir, "keyword2.json"))
    assert os.path.exists(os.path.join(keyword_dir, "bad_keyword_1.json"))

    # Verify executor template files were created
    assert os.path.exists(os.path.join(executor_dir, "executor_one_file.py"))
    assert os.path.exists(os.path.join(executor_dir, "executor_folder.py"))
    assert os.path.exists(os.path.join(executor_dir, "executor_bad_file.py"))
