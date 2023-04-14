import sys

from je_api_testka import execute_action
from je_api_testka import test_record_instance

test_action_list = [
    ["test_api_method",
     {"http_method": "get", "test_url": "http://httpbin.org/get",
      "headers": {
          "x-requested-with": "XMLHttpRequest",
          "Content-Type": "application/x-www-form-urlencoded",
          "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
      }
      }
     ],
    ["test_api_method",
     {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
      "result_check_dict": {"status_code": 200}
      }
     ]
]

try:
    for action_response in execute_action(test_action_list).values():
        response = action_response.get("response_data")
        if response is not None:
            print(response.get("text"))
            print(response.get("start_time"))
            print(response.get("end_time"))
            assert response.get("start_time") is not None
            assert response.get("end_time") is not None

    test_action_list = [
        ["test_api_method", {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"}}],
        ["test_api_method", {"http_method": "post", "test_url": "http://httpbin.org/post"}]
    ]
except Exception as error:
    print(repr(error), file=sys.stderr)
    
try:
    for action_response in execute_action(test_action_list).values():
        response = action_response.get("response_data")
        print(response.get("text"))
except Exception as error:
    print(repr(error), file=sys.stderr)

# soap test
url = "https://www.w3schools.com/xml/tempconvert.asmx"
data = """<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance""" + \
       """" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">""" + \
       """
         <soap12:Body>
           <FahrenheitToCelsius xmlns="https://www.w3schools.com/xml/">
             <Fahrenheit>60</Fahrenheit>
           </FahrenheitToCelsius>
         </soap12:Body>
       </soap12:Envelope>
       """

test_action_list = [
    ["test_api_method", {
        "http_method": "post", "test_url": url, "soap": True, "data": data,
        "result_check_dict": {"status_code": 200}
    }
     ],
]

try:
    for action_response in execute_action(test_action_list).values():
        response = action_response.get("response_data")
        if response is not None:
            print(response.get("text"))
except Exception as error:
    print(repr(error), file=sys.stderr)

test_action_list = [
    ["test_api_method", {"http_method": "dwadawdwaw",
                         "test_url": "http://httpbin.org/post", "params": {"task": "new task"}}],
    ["test_api_method", {"http_method": "dwadwadwadaw", "test_url": "http://httpbin.org/post",
                         "record_request_info": False}]
]

try:
    for action_response in execute_action(test_action_list).values():
        assert action_response is None
except Exception as error:
    print(repr(error), file=sys.stderr)

test_action_list = [
    ["test_api_method", {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"}}],
    ["test_api_method", {"http_method": "post", "test_url": "http://httpbin.org/post",
                         "result_check_dict": {"status_code": 300}}
     ],
    ["generate_html", {"html_file_name": "generate_html_test"}]
]

action_response = execute_action(test_action_list)
try:
    for action_response in execute_action(test_action_list).values():
        if action_response is None:
            pass
        else:
            print(action_response)

except Exception as error:
    print(repr(error), file=sys.stderr)

request_time_list = list()
request_url_list = list()

for i in test_record_instance.test_record_list:
    request_time_list.append(i.get("request_time_sec"))
    request_url_list.append(i.get("request_url"))

print(request_time_list)
print(request_url_list)


