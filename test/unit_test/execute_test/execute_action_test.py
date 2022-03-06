import sys

from je_api_testka import record
from je_api_testka import APITesterExecuteException
from je_api_testka import execute_action

test_action_list = [
    ["test_api_method", {"http_method": "get", "test_url": "http://httpbin.org/get", "headers": {
        'x-requested-with': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    }}],
    ["test_api_method", {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
                         "record_request_info": True}]
]

for action_response in execute_action(test_action_list)[1]:
    response = action_response.get("response_data")
    print(response.get("text"))

test_action_list = [
    ["test_api_method", {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"}}],
    ["test_api_method", {"http_method": "post", "test_url": "http://httpbin.org/post"}]
]

try:
    for action_response in execute_action(test_action_list)[1]:
        response = action_response.get("response_data")
        print(response.get("text"))
except APITesterExecuteException as error:
    print(repr(error), file=sys.stderr)

# soap test
url = "https://www.w3schools.com/xml/tempconvert.asmx"
data = """
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <FahrenheitToCelsius xmlns="https://www.w3schools.com/xml/">
      <Fahrenheit>60</Fahrenheit>
    </FahrenheitToCelsius>
  </soap12:Body>
</soap12:Envelope>
"""

test_action_list = [
    ["test_api_method", {"http_method": "post", "test_url": url, "get_json": False, "soap": True, "data": data}],
]


try:
    for action_response in execute_action(test_action_list)[1]:
        response = action_response.get("response_data")
        print(response.get("text"))
except APITesterExecuteException as error:
    print(repr(error), file=sys.stderr)


test_action_list = [
    ["test_api_method", {"http_method": "dwadawdwaw",
                         "test_url": "http://httpbin.org/post", "params": {"task": "new task"}}],
    ["test_api_method", {"http_method": "dwadwadwadaw", "test_url": "http://httpbin.org/post"}]
]

try:
    for action_response in execute_action(test_action_list)[1]:
        response = action_response.get("response_data")
        print(response.get("text"))
except APITesterExecuteException as error:
    print(repr(error), file=sys.stderr)


print(record.record_list)
print(record.error_record_list)
