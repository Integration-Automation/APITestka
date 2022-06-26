from je_api_testka import reformat_xml_file
from je_api_testka import test_api_method

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

test_result = test_api_method(http_method="post", test_url=url, soap=True, data=data)
print(test_result.get("response_data").get("text"))
print(reformat_xml_file(test_result.get("response_data").get("text")))
print(test_result.get("response_data"))
