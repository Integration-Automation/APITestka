import requests

new_task = {"task": "new task"}

response = requests.post('http://localhost:5000/tasks', params=new_task)

result = response.json()

print(response.status_code)

print(result)

