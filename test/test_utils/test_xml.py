import pytest

from je_api_testka import XMLParser, dict_to_elements_tree, elements_tree_to_dict
from je_api_testka.utils.exception.exceptions import APITesterXMLException

_TEST_XML_STRING = """<?xml version="1.0"?>
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
</data>
"""


def test_xml_parser_from_string():
    """Parse XML from string and verify root element."""
    parser = XMLParser(_TEST_XML_STRING, "string")
    assert parser.xml_root is not None
    assert parser.xml_root.tag == "data"


def test_elements_tree_to_dict():
    """Convert XML tree to dict."""
    parser = XMLParser(_TEST_XML_STRING, "string")
    result = elements_tree_to_dict(parser.xml_root)
    assert isinstance(result, dict)
    assert "data" in result
    countries = result["data"]["country"]
    assert isinstance(countries, list)
    assert len(countries) >= 2


def test_dict_to_elements_tree():
    """Convert dict back to XML string."""
    parser = XMLParser(_TEST_XML_STRING, "string")
    xml_dict = elements_tree_to_dict(parser.xml_root)
    xml_string = dict_to_elements_tree(xml_dict)
    assert isinstance(xml_string, str)
    assert "<data>" in xml_string


def test_roundtrip_xml_dict_xml():
    """Roundtrip: XML -> dict -> XML should preserve structure."""
    parser = XMLParser(_TEST_XML_STRING, "string")
    xml_dict = elements_tree_to_dict(parser.xml_root)
    xml_string = dict_to_elements_tree(xml_dict)
    # Parse the generated XML again to verify it's valid
    parser2 = XMLParser(xml_string, "string")
    assert parser2.xml_root is not None
    assert parser2.xml_root.tag == "data"


_ENTITY_BOMB = """<?xml version="1.0"?>
<!DOCTYPE lolz [<!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;&lol;&lol;">]>
<lolz>&lol2;</lolz>
"""


@pytest.mark.parametrize("text", ["<data><unclosed></data>", _ENTITY_BOMB], ids=["malformed", "entity-expansion"])
def test_xml_parser_from_string_rejects_bad_xml(text):
    with pytest.raises(APITesterXMLException) as caught:
        XMLParser(text, "string")
    assert caught.value.__cause__ is not None


def test_xml_parser_from_file_rejects_a_missing_file(tmp_path):
    with pytest.raises(APITesterXMLException) as caught:
        XMLParser(str(tmp_path / "absent.xml"), "file")
    assert isinstance(caught.value.__cause__, OSError)


def test_xml_parser_from_file_reads_a_file(tmp_path):
    path = tmp_path / "data.xml"
    path.write_text(_TEST_XML_STRING, encoding="utf-8")
    assert XMLParser(str(path), "file").xml_root.tag == "data"
