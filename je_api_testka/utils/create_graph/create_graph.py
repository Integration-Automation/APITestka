from typing import Tuple

try:
    from je_matplotlib_wrapper import set_tkinter_embed_matplotlib_barh
except ImportError as error:
    raise ImportError(repr(error) + " you need install je_matplotlib_wrapper to use this")

from tkinter import Tk

from je_api_testka.utils.test_record.record_test_result_class import test_record


def get_list(get_data_horizontal: str, get_data_vertical: str) -> Tuple[list, list]:
    list_vertical = list()
    list_horizontal = list()
    for i in test_record.record_list:
        list_vertical.append(i.get(get_data_vertical))
        list_horizontal.append(i.get(get_data_horizontal))
    return list_vertical, list_horizontal


def make_tkinter_request_time_graph():
    show_data = get_list("request_time_sec", "request_url")
    set_tkinter_embed_matplotlib_barh(
        y_content_list=show_data[0],
        x_content_list=show_data[1],
        show_figure_window=Tk(),
    )
