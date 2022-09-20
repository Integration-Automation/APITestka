from tkinter import Tk
from typing import Tuple

from je_api_testka.utils.test_record.test_record_class import test_record_instance


def get_list(get_data_horizontal: str, get_data_vertical: str) -> Tuple[list, list]:
    list_vertical = list()
    list_horizontal = list()
    for i in test_record_instance.test_record_list:
        list_vertical.append(i.get(get_data_vertical))
        list_horizontal.append(i.get(get_data_horizontal))
    return list_vertical, list_horizontal


def make_tkinter_request_time_graph():
    try:
        from je_tk_plot import set_tkinter_embed_matplotlib_barh
    except ImportError as error:
        raise ImportError(repr(error) + " you need install je_tk_plot to use this")
    show_data: Tuple[list, list] = get_list("request_time_sec", "request_url")
    set_tkinter_embed_matplotlib_barh(
        y_content_list=show_data[0],
        x_content_list=show_data[1],
        show_figure_window=Tk(),
    )
