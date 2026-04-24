from collections import defaultdict
# Used for XML serialization only (Element/SubElement/tostring); defusedxml does not
# provide write APIs. Inputs come from internal dicts, never from untrusted XML data.
from xml.etree import ElementTree  # nosec B405  # nosemgrep: python.lang.security.use-defused-xml.use-defused-xml

from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def _collapse_children(children) -> dict:
    """Recursively collapse children into a {tag: value | [values]} mapping."""
    grouped = defaultdict(list)
    for child_dict in map(elements_tree_to_dict, children):
        for key, value in child_dict.items():
            grouped[key].append(value)
    return {key: value[0] if len(value) == 1 else value for key, value in grouped.items()}


def _apply_text(elements_dict: dict, tag, text_raw: str, has_children: bool, has_attrib: bool) -> None:
    """Apply element text into the result dict, respecting children/attrib presence."""
    text = text_raw.strip()
    if has_children or has_attrib:
        if text:
            elements_dict[tag]['#text'] = text
    else:
        elements_dict[tag] = text


def elements_tree_to_dict(elements_tree) -> dict:
    """
    將 XML 樹結構轉換為字典
    Convert XML tree structure into dictionary

    :param elements_tree: XML 樹節點 / XML tree node
    :return: 對應的字典結構 / Dictionary representation of XML
    """
    apitestka_logger.info(f"change_xml_structure.py elements_tree_to_dict elements_tree: {elements_tree}")

    tag = elements_tree.tag
    has_attrib = bool(elements_tree.attrib)
    elements_dict: dict = {tag: {} if has_attrib else None}

    children = list(elements_tree)
    if children:
        elements_dict = {tag: _collapse_children(children)}

    if has_attrib:
        elements_dict[tag].update(
            ('@' + key, value) for key, value in elements_tree.attrib.items()
        )

    if elements_tree.text:
        _apply_text(elements_dict, tag, elements_tree.text, bool(children), has_attrib)

    return elements_dict


def _set_text_marker(root, key: str, value) -> None:
    if key != '#text' or not isinstance(value, str):
        raise ValueError(f"Only '#text' key with str value is allowed, got key={key!r}")
    root.text = value


def _set_attribute(root, key: str, value) -> None:
    if not isinstance(value, str):
        raise TypeError(f"XML attribute value must be str, got {type(value).__name__}")
    root.set(key[1:], value)


def _handle_dict_entry(key, value, root) -> None:
    if not isinstance(key, str):
        raise TypeError(f"XML dict key must be str, got {type(key).__name__}")
    if key.startswith('#'):
        _set_text_marker(root, key, value)
    elif key.startswith('@'):
        _set_attribute(root, key, value)
    elif isinstance(value, list):
        for elements in value:
            _to_elements_tree(elements, ElementTree.SubElement(root, key))
    else:
        _to_elements_tree(value, ElementTree.SubElement(root, key))


def _to_elements_tree(json_dict, root) -> None:
    if isinstance(json_dict, str):
        root.text = json_dict
    elif isinstance(json_dict, dict):
        for key, value in json_dict.items():
            _handle_dict_entry(key, value, root)
    else:
        raise TypeError('invalid type: ' + str(type(json_dict)))


def dict_to_elements_tree(json_dict: dict) -> str:
    """
    將字典轉換為 XML 字串
    Convert dictionary into XML string

    :param json_dict: JSON 字典 / JSON dictionary
    :return: XML 字串 / XML string
    """
    apitestka_logger.info(f"change_xml_structure.py dict_to_elements_tree json_dict: {json_dict}")

    if not isinstance(json_dict, dict) or len(json_dict) != 1:
        raise ValueError("json_dict must be a dict with exactly one root element")
    tag, body = next(iter(json_dict.items()))
    node = ElementTree.Element(tag)
    _to_elements_tree(body, node)

    return str(ElementTree.tostring(node), encoding="utf-8")
