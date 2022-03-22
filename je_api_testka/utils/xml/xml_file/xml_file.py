import xml.dom.minidom
from xml.etree import ElementTree
from collections import defaultdict

from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_cant_read_xml_error
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_xml_type_error
from je_api_testka.utils.exception.api_test_exceptions import APITesterXMLException
from je_api_testka.utils.exception.api_test_exceptions import APITesterXMLTypeException


def reformat_xml_file(xml_string: str):
    dom = xml.dom.minidom.parseString(xml_string)
    return dom.toprettyxml()


class XMLParser(object):

    def __init__(self, xml_string: str, xml_type: str):
        self.element_tree = ElementTree
        self.tree = None
        self.xml_root = None
        self.xml_from_type = "string"
        self.xml_string = xml_string.strip()
        xml_type = xml_type.lower()
        if xml_type not in ["file", "string"]:
            raise APITesterXMLTypeException(api_test_xml_type_error)
        if xml_type == "string":
            self.xml_parser_from_string()
        else:
            self.xml_parser_from_file()

    def xml_parser_from_string(self, **kwargs):
        try:
            self.xml_root = ElementTree.fromstring(self.xml_string, **kwargs)
        except APITesterXMLException:
            raise APITesterXMLException(api_test_cant_read_xml_error)
        return self.xml_root

    def xml_parser_from_file(self, **kwargs):
        try:
            self.tree = ElementTree.parse(self.xml_string, **kwargs)
        except APITesterXMLException:
            raise APITesterXMLException(api_test_cant_read_xml_error)
        self.xml_root = self.tree.getroot()
        self.xml_from_type = "file"
        return self.xml_root

    def iter(self, tag_name: [str, None] = None):
        if self.xml_from_type == "string":
            return self.xml_root.iter(tag_name)
        else:
            return self.tree.iter(tag_name)

    def xml_iterparse(self, xml_string: str, **kwargs):
        return self.element_tree.iterparse(xml_string, **kwargs)

    def write_xml(self, write_xml_filename: str, write_content: str):
        write_content = write_content.strip()
        content = self.element_tree.fromstring(write_content)
        tree = self.element_tree.ElementTree(content)
        tree.write(write_xml_filename, encoding="utf-8")


def elements_tree_to_dict(elements_tree):
    elements_dict = {elements_tree.tag: {} if elements_tree.attrib else None}
    children = list(elements_tree)
    if children:
        default_dict = defaultdict(list)
        for dc in map(elements_tree_to_dict, children):
            for key, value in dc.items():
                default_dict[key].append(value)
        elements_dict = {elements_tree.tag: {key: value[0] if len(value) == 1 else value
                                             for key, value in default_dict.items()}}
    if elements_tree.attrib:
        elements_dict[elements_tree.tag].update(('@' + key, value) for key, value in elements_tree.attrib.items())
    if elements_tree.text:
        text = elements_tree.text.strip()
        if children or elements_tree.attrib:
            if text:
                elements_dict[elements_tree.tag]['#text'] = text
        else:
            elements_dict[elements_tree.tag] = text
    return elements_dict


def dict_to_elements_tree(json_dict):
    def _to_elements_tree(json_dict, root):
        if not json_dict:
            pass
        elif isinstance(json_dict, str):
            root.text = json_dict
        elif isinstance(json_dict, dict):
            for key, value in json_dict.items():
                assert isinstance(key, str)
                if key.startswith('#'):
                    assert key == '#text' and isinstance(value, str)
                    root.text = value
                elif key.startswith('@'):
                    assert isinstance(value, str)
                    root.set(key[1:], value)
                elif isinstance(value, list):
                    for elements in value:
                        _to_elements_tree(elements, ElementTree.SubElement(root, key))
                else:
                    _to_elements_tree(value, ElementTree.SubElement(root, key))
        else:
            raise TypeError('invalid type: ' + str(type(json_dict)))
    assert isinstance(json_dict, dict) and len(json_dict) == 1
    tag, body = next(iter(json_dict.items()))
    node = ElementTree.Element(tag)
    _to_elements_tree(body, node)
    return str(ElementTree.tostring(node), encoding="utf-8")

