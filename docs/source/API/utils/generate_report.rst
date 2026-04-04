===============
Generate Report
===============

HTML
----

.. code-block:: python

   def generate_html():
       """
       :return: test success_list & test failure_list
       """

   def generate_html_report(html_file_name: str = "default_name"):
       """
       :param html_file_name: output HTML file name
       """

JSON
----

.. code-block:: python

   def generate_json():
       """
       :return: test success_dict, test failure_dict
       """

   def generate_json_report(json_file_name: str = "default_name"):
       """
       :param json_file_name: output JSON file name
       """

XML
---

.. code-block:: python

   def generate_xml():
       """
       :return: success_xml_string, failure_xml_string
       """

   def generate_xml_report(xml_file_name: str = "default_name"):
       """
       :param xml_file_name: output XML file name
       """
