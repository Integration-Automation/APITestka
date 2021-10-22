import requests

put_task = "/task2"

new_task = {"task": "new task"}

response = requests.put('http://localhost:5000/tasks' + put_task, params=new_task)


