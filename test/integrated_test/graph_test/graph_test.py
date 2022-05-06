import sys

from je_api_testka import make_tkinter_request_time_graph
from je_api_testka import execute_action
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
except Exception as error:
    print(repr(error), file=sys.stderr)

try:
    make_tkinter_request_time_graph()
except Exception as error:
    print(repr(error))
    print("yep this should be raise an exception")
