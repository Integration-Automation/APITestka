import os

print(os.getcwd())

os.system("cd " + os.getcwd())
os.system("python -m je_api_testka --execute_file " + os.getcwd() + r"/test/unit_test/argparse/test1.json")
os.system("python -m je_api_testka --execute_dir " + os.getcwd() + r"/test/unit_test/argparse")
