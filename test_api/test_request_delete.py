import requests

delete_task = "/task3"

response = requests.delete('http://localhost:5000/tasks'+ delete_task)

print(response.status_code)

