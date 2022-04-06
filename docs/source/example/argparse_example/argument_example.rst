==================
APITestka Argument Example
==================

.. code-block:: python

    """
    cd to workdir
    python je_api_testka + action file path
    """
    import os

    print(os.getcwd())

    os.system("cd " + os.getcwd())
    os.system("python je_api_testka --execute_file " + os.getcwd() + r"/test/unit_test/argparse/test.json")