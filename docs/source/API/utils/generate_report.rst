Generate Report API
----

.. code-block:: python

    def generate_html():
        """
        :return: test success_list & test failure_list
        """

.. code-block:: python

    def generate_html_report(html_file_name: str = "default_name"):
        """
        :param html_file_name: save html file name
        :return:
        """

.. code-block:: python

    def generate_json():
        """
        :return: test success_dict test failure_dict
        """

.. code-block:: python

    def generate_json_report(json_file_name: str = "default_name"):
        """
        :param json_file_name: save json file's name
        """

.. code-block:: python

    def generate_xml():
        """
        :return: success_xml_string, failure_xml_string
        """

.. code-block:: python

    def generate_xml_report(xml_file_name: str = "default_name"):
        """
        :param xml_file_name: save xml file with xml_file_name
        """