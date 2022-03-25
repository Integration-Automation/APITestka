import os

print(os.getcwd())

os.system("cd " + os.getcwd())
os.system("python -m je_api_testka " + os.getcwd() + r"\test.json")


