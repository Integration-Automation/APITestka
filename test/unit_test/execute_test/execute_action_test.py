from je_api_testka import execute_action

test_action_list = [
    ("get", "http://httpbin.org/get", False, {"headers": {
        'x-requested-with': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    }}),
    ("post", "http://httpbin.org/post", False, {"params": {"task": "new task"}})
]
for action_response in execute_action(test_action_list)[1]:
    response = action_response.get("response_data")
    print(response.get("text"))
