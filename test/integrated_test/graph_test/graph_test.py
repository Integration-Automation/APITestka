from je_api_testka import (execute_action, APITesterExecuteException, record)
import sys

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
    ["test_api_method", {"http_method": "post", "test_url": url, "soap": True, "data": data}],
]

try:
    for action_response in execute_action(test_action_list)[1]:
        response = action_response.get("response_data")
        print(response.get("text"))
except APITesterExecuteException as error:
    print(repr(error), file=sys.stderr)

print(record.record_list)
print(record.error_record_list)

request_time_list = list()
request_url_list = list()

for i in record.record_list:
    request_time_list.append(i.get("request_time_sec"))
    request_url_list.append(i.get("request_url"))

print(request_time_list)
print(request_url_list)

from je_matplotlib_wrapper import set_tkinter_embed_matplotlib_barh
from tkinter import Tk

set_tkinter_embed_matplotlib_barh(y_content_list=request_url_list,
                                  x_content_list=request_time_list,
                                  show_figure_window=Tk(),
                                  )
