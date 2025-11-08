from collections import defaultdict
from xml.etree import ElementTree

from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def elements_tree_to_dict(elements_tree) -> dict:
    """
    將 XML 樹結構轉換為字典
    Convert XML tree structure into dictionary

    :param elements_tree: XML 樹節點 / XML tree node
    :return: 對應的字典結構 / Dictionary representation of XML
    """
    apitestka_logger.info(f"change_xml_structure.py elements_tree_to_dict elements_tree: {elements_tree}")

    # 初始化字典，若有屬性則為空 dict，否則為 None
    # Initialize dict: empty if attributes exist, else None
    elements_dict: dict = {elements_tree.tag: {} if elements_tree.attrib else None}

    # 取得子節點 / Get children nodes
    children: list = list(elements_tree)
    if children:
        default_dict = defaultdict(list)
        # 遞迴處理子節點 / Recursively process children
        for dc in map(elements_tree_to_dict, children):
            for key, value in dc.items():
                default_dict[key].append(value)
        # 若同名子節點只有一個，直接取值；否則保留為 list
        # If only one child with same tag, use value directly; else keep as list
        elements_dict: dict = {
            elements_tree.tag: {key: value[0] if len(value) == 1 else value for key, value in default_dict.items()}
        }

    # 處理屬性，將其加入字典，並以 '@' 作為前綴
    # Handle attributes, add to dict with '@' prefix
    if elements_tree.attrib:
        elements_dict[elements_tree.tag].update(
            ('@' + key, value) for key, value in elements_tree.attrib.items()
        )

    # 處理文字內容 / Handle text content
    if elements_tree.text:
        text = elements_tree.text.strip()
        if children or elements_tree.attrib:
            if text:
                elements_dict[elements_tree.tag]['#text'] = text
        else:
            elements_dict[elements_tree.tag] = text

    return elements_dict


def dict_to_elements_tree(json_dict: dict) -> str:
    """
    將字典轉換為 XML 字串
    Convert dictionary into XML string

    :param json_dict: JSON 字典 / JSON dictionary
    :return: XML 字串 / XML string
    """
    apitestka_logger.info(f"change_xml_structure.py dict_to_elements_tree json_dict: {json_dict}")

    def _to_elements_tree(json_dict: dict, root):
        # 若為字串，直接設為節點文字 / If string, set as node text
        if isinstance(json_dict, str):
            root.text = json_dict
        elif isinstance(json_dict, dict):
            for key, value in json_dict.items():
                assert isinstance(key, str)
                if key.startswith('#'):
                    # 特殊標記 '#text' 表示文字內容 / Special key '#text' means text content
                    assert key == '#text' and isinstance(value, str)
                    root.text = value
                elif key.startswith('@'):
                    # 特殊標記 '@' 表示屬性 / Special key '@' means attribute
                    assert isinstance(value, str)
                    root.set(key[1:], value)
                elif isinstance(value, list):
                    # 若值為 list，建立多個子節點 / If value is list, create multiple sub-elements
                    for elements in value:
                        _to_elements_tree(elements, ElementTree.SubElement(root, key))
                else:
                    # 遞迴建立子節點 / Recursively create sub-element
                    _to_elements_tree(value, ElementTree.SubElement(root, key))
        else:
            raise TypeError('invalid type: ' + str(type(json_dict)))

    # 確保字典只有一個根節點 / Ensure dict has only one root element
    assert isinstance(json_dict, dict) and len(json_dict) == 1
    tag, body = next(iter(json_dict.items()))
    node = ElementTree.Element(tag)
    _to_elements_tree(body, node)

    # 將 XML 轉換為字串並回傳 / Convert XML to string and return
    return str(ElementTree.tostring(node), encoding="utf-8")