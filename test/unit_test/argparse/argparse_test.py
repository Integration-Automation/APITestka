import os

print(os.getcwd())

os.system("cd " + os.getcwd())
os.system("python je_api_testka " + os.getcwd() + r"/test/unit_test/argparse/test.json")


