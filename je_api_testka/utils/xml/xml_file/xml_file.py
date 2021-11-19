from xml.etree import ElementTree

from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_cant_read_xml_error
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_xml_type_error
from je_api_testka.utils.exception.api_test_exceptions import APITesterXMLException
from je_api_testka.utils.exception.api_test_exceptions import APITesterXMLTypeException


class XMLParser(object):

    def __init__(self, xml_string: str, type: str):
        self.element_tree = ElementTree
        self.tree = None
        self.xml_root = None
        self.xml_from = "string"
        self.xml_string = xml_string.strip()
        type = type.lower()
        if type not in ["file", "string"]:
            raise APITesterXMLTypeException(api_test_xml_type_error)
        if type == "string":
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
        self.xml_from = "file"
        return self.xml_root

    def find_tag(self, tag_name: [str, None] = None):
        if self.xml_from == "string":
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
