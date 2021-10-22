import requests

response = requests.get('http://localhost:5000/tasks')

result = response.json()

print(response.status_code)

print(result)

