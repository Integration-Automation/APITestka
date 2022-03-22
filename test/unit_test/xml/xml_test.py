from je_api_testka import XMLParser
from je_api_testka import elements_tree_to_dict
from je_api_testka import dict_to_elements_tree
from pprint import pprint

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
