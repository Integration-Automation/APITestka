import xml.dom.minidom
from xml.etree import ElementTree

from je_api_testka.utils.exception.exception_tags import cant_read_xml_error, xml_type_error
from je_api_testka.utils.exception.exceptions import APITesterXMLException, APITesterXMLTypeException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def reformat_xml_file(xml_string: str):
    """
    將 XML 字串重新排版為易讀格式
    Reformat XML string into pretty-printed format

    :param xml_string: 原始 XML 字串 / Raw XML string
    :return: 格式化後的 XML 字串 / Pretty-printed XML string
    """
    dom = xml.dom.minidom.parseString(xml_string)
    return dom.toprettyxml()


class XMLParser(object):
    """
    XML 解析器類別，用來處理字串或檔案形式的 XML
    XML parser class to handle XML from string or file
    """

    def __init__(self, xml_string: str, xml_type: str = "string"):
        """
        初始化 XMLParser
        Initialize XMLParser

        :param xml_string: 完整 XML 字串或檔案路徑 / Full XML string or file path
        :param xml_type: "file" 或 "string"，決定解析來源 / "file" or "string" to specify source type
        """
        apitestka_logger.info(f"Init XMLParser xml_string: {xml_string} xml_type: {xml_type}")
        self.element_tree = ElementTree
        self.tree = None
        self.xml_root = None
        self.xml_from_type = "string"
        self.xml_string = xml_string.strip()

        xml_type = xml_type.lower()
        if xml_type not in ["file", "string"]:
            # 若傳入的 xml_type 非法，拋出例外
            # Raise exception if xml_type is invalid
            raise APITesterXMLTypeException(xml_type_error)

        if xml_type == "string":
            self.xml_parser_from_string()
        else:
            self.xml_parser_from_file()

    def xml_parser_from_string(self, **kwargs):
        """
        從字串解析 XML
        Parse XML from string

        :param kwargs: 額外參數 / Additional parameters
        :return: XML 根節點 / XML root element
        """
        apitestka_logger.info(f"XMLParser xml_parser_from_string kwargs: {kwargs}")
        try:
            self.xml_root = ElementTree.fromstring(self.xml_string, **kwargs)
        except APITesterXMLException:
            raise APITesterXMLException(cant_read_xml_error)
        return self.xml_root

    def xml_parser_from_file(self, **kwargs):
        """
        從檔案解析 XML
        Parse XML from file

        :param kwargs: 額外參數 / Additional parameters
        :return: XML 根節點 / XML root element
        """
        apitestka_logger.info(f"XMLParser xml_parser_from_file kwargs: {kwargs}")
        try:
            self.tree = ElementTree.parse(self.xml_string, **kwargs)
        except APITesterXMLException:
            raise APITesterXMLException(cant_read_xml_error)
        self.xml_root = self.tree.getroot()
        self.xml_from_type = "file"
        return self.xml_root

    def write_xml(self, write_xml_filename: str, write_content: str):
        """
        將 XML 字串寫入檔案
        Write XML string into file

        :param write_xml_filename: 輸出檔案名稱 / Output file name
        :param write_content: 要寫入的 XML 內容 / XML content to write
        """
        write_content = write_content.strip()
        content = self.element_tree.fromstring(write_content)
        tree = self.element_tree.ElementTree(content)
        tree.write(write_xml_filename, encoding="utf-8")