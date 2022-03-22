==================
APITestka XML Doc
==================

.. code-block:: python

    class XMLParser(object):
        def __init__(self, xml_string: str, xml_type: str):
    """
    xml_string: verify xml string
    xml_type: "string" or "file"
    """

    def elements_tree_to_dict(elements_tree):
    """
    elements_tree: full xml elements tree like XMLParser.xml_root
    return xml to dict
    """
    def dict_to_elements_tree(json_dict):
    """
    json_dict: dict
    return dict to xml string
    """
