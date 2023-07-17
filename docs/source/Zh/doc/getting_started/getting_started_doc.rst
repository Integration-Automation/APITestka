開始使用
----

首先，創建專案。

在 APITestka 裡可以創建專案，創建專案後將會自動生成範例文件，
範例文件包含 python executor 檔案以及 keyword.json 檔案。

要創建專案可以用以下方式:

.. code-block:: python

    from je_api_testka import create_project_dir
    # create on current workdir
    create_project_dir()
    # create project on project_path
    create_project_dir("project_path")
    # create project on project_path and dir name is My First Project
    create_project_dir("project_path", "My First Project")

或是這個方式將會在 project_path 路徑產生專案

.. code-block:: console

    python -m je_api_testka --create_project project_path

然後可以進入專案資料夾，executor 資料夾，選擇其中一個 executor 執行並觀察，
keyword 資料夾裡的 keyword json 檔案定義了要執行的動作。

如果想要透過純 python 來執行的話可以參考以下範例:

注意! 只能使用以下 HTTP Method ["get", "post", "put", "patch", "delete", "head", "options"]

.. code-block:: python

    from je_api_testka import execute_files

    test_api_list = [
    ["AT_test_api_method",
     {
         "http_method": "post",
         "test_url": "http://httpbin.org/post",
         "params": {"task": "new task"},
         "result_check_dict": {"status_code": 200}
     }
     ],
    ["AT_test_api_method",
     {
         "http_method": "get",
         "test_url": "http://httpbin.org/post",
         "result_check_dict": {"status_code": 405}
     }
     ]
    ]