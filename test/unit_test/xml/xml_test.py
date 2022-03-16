import sys
import xml.etree.ElementTree

from je_api_testka import XMLParser
from je_api_testka import elements_tree_to_dict
from je_api_testka import dict_to_elements_tree


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


test_xml_string = \
    """
        <?xml version="1.0"?>
        <data>
            <test_data name="test_use_1">test</test_data>
            <test_data name="test_use_2">test output</test_data>
            <test_data name="test_use_3">test text</test_data>
        </data>
    """

xml_parse = process_xml_test(test_xml_string, "string")

xml_parse.write_xml("test.xml", "<test name='test'></test>")

xml_parse = process_xml_test("test.xml", "file")

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

try:
    test_xml_string = \
        """
            wdadwdadwwawdwdawdwafmjawk;gkA:OH？lmkjha'l[wmjho[
            jaHWOdwadwk;ajdwakdjda;awdkjl;jaw;daj;adjwda;jfgoa:KNWHiughdwa
            MJw;pkgh
            wpahkw'[spmjhaMJHW"{AML"OW
            jWL"{jhao[wja[who
            ja[lwjhm[W"JHahjm
        """
    process_xml_test(test_xml_string, "string")
except xml.etree.ElementTree.ParseError as error:
    print(repr(error), file=sys.stderr)

test_xml_string = \
    """
        <?xml version="1.0"?>
        <data>
        </data>
    """
process_xml_test(test_xml_string, "string")

test_xml_string = \
    """
        <?xml version="1.0"?>
        <data>
        '"''dwl;dwa;ldkawdl;kdwal;dk;lawd
        </data>
    """
process_xml_test(test_xml_string, "string")

try:
    test_xml_string = \
        """
            <?xml version="1.0"?>
            dwadwadwaadwdadwdwa
        """
    process_xml_test(test_xml_string, "string")
except xml.etree.ElementTree.ParseError as error:
    print(repr(error), file=sys.stderr)

test_xml_string = \
    """
        <?xml version="1.0"?>
        <data>
            <test_data name="test_use_1">test</test_data>
            <test_data name="test_use_2">test output</test_data>
            <test_data name="test_use_3">test text</test_data>
        </data>
    """

process_xml_parse = XMLParser(test_xml_string, "string")
print(process_xml_parse.xml_root.tag)
print(process_xml_parse.xml_root.attrib)
print(process_xml_parse.xml_root.text)
print(type(process_xml_parse.xml_root))
for test_data in process_xml_parse.iter("test_data"):
    print(test_data.attrib)
    print(test_data.text)

print("-------")

from xml.etree import cElementTree as ET
e = ET.XML('''
<root>
  <e />
  <e>text</e>
  <e name="value" />
  <e name="value">text</e>
  <e> <a>text</a> <b>text</b> </e>
  <e> <a>text</a> <a>text</a> </e>
  <e> text <a>text</a> </e>
</root>
''')

from pprint import pprint
pprint(elements_tree_to_dict(e))

dict_test_xml_string = \
"""<?xml version="1.0"?>
<data>
    <country name="Liechtenstein">
        <rank>1</rank>
        <year>2008</year>
        <gdppc>141100</gdppc>
        <neighbor name="Austria" direction="E"/>
        <neighbor name="Switzerland" direction="W"/>
    </country>
    <country name="Singapore">
        <rank>4</rank>
        <year>2011</year>
        <gdppc>59900</gdppc>
        <neighbor name="Malaysia" direction="N"/>
    </country>
    <country name="Panama">
        <rank>68</rank>
        <year>2011</year>
        <gdppc>13600</gdppc>
        <neighbor name="Costa Rica" direction="W"/>
        <neighbor name="Colombia" direction="E"/>
    </country>
</data>
"""

process_xml_parse = XMLParser(dict_test_xml_string, "string")
xml_to_json = elements_tree_to_dict(process_xml_parse.xml_root)
pprint(xml_to_json)
json_to_xml = dict_to_elements_tree(xml_to_json)
pprint(json_to_xml)
process_xml_parse = XMLParser(dict_test_xml_string, "string")
