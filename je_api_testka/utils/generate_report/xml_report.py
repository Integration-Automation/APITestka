from threading import Lock
from typing import Tuple
from xml.dom.minidom import parseString

from je_api_testka.utils.generate_report.json_report import generate_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.xml.change_xml_structure.change_xml_structure import dict_to_elements_tree


def generate_xml() -> Tuple[str, str]:
    """
    生成 XML 格式的字串，分為成功與失敗的測試紀錄
    Generate XML formatted strings for success and failure test records

    :return: (success_xml_string, failure_xml_string)
    """
    apitestka_logger.info("xml_report.py generate_xml")

    # 從 JSON 報告生成成功與失敗的字典
    # Generate success and failure dictionaries from JSON report
    success_dict, failure_dict = generate_json()

    # 包裝成 xml_data 根節點
    # Wrap into xml_data root node
    success_dict = dict({"xml_data": success_dict})
    failure_dict = dict({"xml_data": failure_dict})

    # 將 dict 轉換為 XML 結構字串
    # Convert dict to XML structure string
    success_json_to_xml = dict_to_elements_tree(success_dict)
    failure_json_to_xml = dict_to_elements_tree(failure_dict)

    return success_json_to_xml, failure_json_to_xml


def generate_xml_report(xml_file_name: str = "default_name") -> None:
    """
    生成 XML 報告檔案，分別輸出成功與失敗紀錄
    Generate XML report files, outputting success and failure records separately

    :param xml_file_name: 儲存的檔案名稱 (不含副檔名)
                          File name to save (without extension)
    """
    apitestka_logger.info(f"xml_report.py generate_xml_report xml_file_name: {xml_file_name}")

    # 取得成功與失敗的 XML 字串
    # Get success and failure XML strings
    success_xml, failure_xml = generate_xml()

    # 使用 minidom 美化 XML 格式
    # Use minidom to pretty-print XML
    success_xml = parseString(success_xml)
    failure_xml = parseString(failure_xml)
    success_xml = success_xml.toprettyxml()
    failure_xml = failure_xml.toprettyxml()

    lock = Lock()

    # 儲存失敗紀錄 XML / Save failure XML
    try:
        lock.acquire()
        with open(xml_file_name + "_failure.xml", "w+") as file_to_write:
            file_to_write.write(failure_xml)
    except Exception as error:
        apitestka_logger.error(
            f"generate_xml_report, xml_file_name: {xml_file_name}, failed: {repr(error)}"
        )
    finally:
        lock.release()

    # 儲存成功紀錄 XML / Save success XML
    try:
        lock.acquire()
        with open(xml_file_name + "_success.xml", "w+") as file_to_write:
            file_to_write.write(success_xml)
    except Exception as error:
        apitestka_logger.error(
            f"generate_xml_report, xml_file_name: {xml_file_name}, failed: {repr(error)}"
        )
    finally:
        lock.release()