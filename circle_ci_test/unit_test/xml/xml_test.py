from je_api_testka import XMLParser

test_xml_string = \
    """
        <?xml version="1.0"?>
        <data>
            <test_data name="test_use_1">test</test_data>
            <test_data name="test_use_2">test output</test_data>
            <test_data name="test_use_3">test text</test_data>
        </data>
    """

xml_parse = XMLParser(test_xml_string, "string")
for child in xml_parse.find_tag():
    child_content = [child.tag, child.attrib, child.text]
    for content in child_content:
        if content is not None:
            print(content, end=" ")
        else:
            continue
    print()

print()

xml_parse.write_xml("test.xml", "<test name='test'></test>")

xml_parse = XMLParser("test.xml", "file")
for child in xml_parse.find_tag():
    child_content = [child.tag, child.attrib, child.text]
    for content in child_content:
        if content is not None:
            print(content, end=" ")
        else:
            continue
    print()

print()

for event, elements in xml_parse.xml_iterparse("test.xml"):
    if event == "end":
        child_content = [elements.tag, elements.attrib, elements.text]
        for content in child_content:
            if content is not None:
                print(content, end=" ")
            else:
                continue
        print()
    elements.clear()


