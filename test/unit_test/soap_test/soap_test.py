from je_api_testka import reformat_xml_file
from je_api_testka import test_api_method

from je_api_testka import XMLParser
from je_api_testka import elements_tree_to_dict

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


def process_xml_test(xml_string_or_file, xml_type):
    process_xml_parse = XMLParser(xml_string_or_file, xml_type)
    for child in process_xml_parse.iter():
        process_child_content = [child.tag, child.attrib, child.text]
        for process_content in process_child_content:
            if process_content is not None:
                print(process_content, end=" ")
            else:
                continue
        print()
    print()
    return process_xml_parse


xml_parse = process_xml_test(test_result.get("response_data").get("text"), "string")
print(elements_tree_to_dict(xml_parse.xml_root))
