import sys

from je_api_testka import test_record
from je_api_testka.utils.exception.api_test_exceptions import HTMLException
from je_api_testka.utils.exception.api_test_eceptions_tag import html_generate_no_data_tag
from threading import Lock

lock = Lock()

html_string = \
    r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <title>api_testka_report</title>

    <style>
        .main_table {{
            margin: 0 auto;
            border-collapse: collapse;
            width: 75%;
        }}

        .success_table_head {{
            border: 3px solid #262626;
            background-color: aqua;
            font-family: "Times New Roman", sans-serif;
            text-align: center;
        }}

        .failure_table_head {{
            border: 3px solid #262626;
            background-color: #f84c5f;
            font-family: "Times New Roman", sans-serif;
            text-align: center;
        }}

        .table_data_field_title {{
            border: 3px solid #262626;
            padding: 0;
            margin: 0;
            background-color: #dedede;
            font-family: "Times New Roman", sans-serif;
            text-align: center;
            width: 25%;
        }}

        .table_data_field_text {{
            border: 3px solid #262626;
            padding: 0;
            margin: 0;
            background-color: #dedede;
            font-family: "Times New Roman", sans-serif;
            text-align: left;
            width: 75%;
        }}

        .text {{
            text-align: center;
            font-family: "Times New Roman", sans-serif;
        }}
    </style>
</head>
<body>
<h3 class="text">
    Success
</h3>
{success_table}
<h3 class="text">
    Failure
</h3>
{failure_table}
</body>
</html>
""".strip()

success_table = \
    r"""
    <table class="main_table">
        <thead>
        <tr>
            <th colspan="2" class="success_table_head">Test Report</th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <td class="table_data_field_title">status_code</td>
            <td class="table_data_field_text">{status_code}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">text</td>
            <td class="table_data_field_text">{text}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">content</td>
            <td class="table_data_field_text">{content}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">headers</td>
            <td class="table_data_field_text">{headers}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">history</td>
            <td class="table_data_field_text">{history}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">encoding</td>
            <td class="table_data_field_text">{encoding}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">cookies</td>
            <td class="table_data_field_text">{cookies}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">elapsed</td>
            <td class="table_data_field_text">{elapsed}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">request_time_sec</td>
            <td class="table_data_field_text">{request_time_sec}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">request_method</td>
            <td class="table_data_field_text">{request_method}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">request_url</td>
            <td class="table_data_field_text">{request_url}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">request_body</td>
            <td class="table_data_field_text">{request_body}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">start_time</td>
            <td class="table_data_field_text">{start_time}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">end_time</td>
            <td class="table_data_field_text">{end_time}</td>
        </tr>
        </tbody>
    </table>
    """.strip()

failure_table = \
    r"""
    <table class="main_table">
    <thead>
    <tr>
        <th colspan="2" class="failure_table_head">Test Report</th>
    </tr>
    </thead>
    <tbody>
    <tr>
        <td class="table_data_field_title">http_method</td>
        <td class="table_data_field_text">{http_method}</td>
    </tr>
    <tr>
        <td class="table_data_field_title">test_url</td>
        <td class="table_data_field_text">{test_url}</td>
    </tr>
    <tr>
        <td class="table_data_field_title">soap</td>
        <td class="table_data_field_text">{soap}</td>
    </tr>
    <tr>
        <td class="table_data_field_title">record_request_info</td>
        <td class="table_data_field_text">{record_request_info}</td>
    </tr>
    <tr>
        <td class="table_data_field_title">clean_record</td>
        <td class="table_data_field_text">{clean_record}</td>
    </tr>
    <tr>
        <td class="table_data_field_title">result_check_dict</td>
        <td class="table_data_field_text">{result_check_dict}</td>
    </tr>
    <tr>
        <td class="table_data_field_title">error</td>
        <td class="table_data_field_text">{error}</td>
    </tr>
    </tbody>
</table>
    """.strip()


def generate_html(html_name: str):
    """
    :param html_name: save html file name
    :return: html_string
    """
    if len(test_record.record_list) == 0:
        raise HTMLException(html_generate_no_data_tag)
    else:
        success = ""
        for record_data in test_record.record_list:
            success = "".join(
                [
                    success,
                    success_table.format(
                        status_code=record_data.get("status_code"),
                        text=record_data.get("text"),
                        content=record_data.get("content"),
                        headers=record_data.get("headers"),
                        history=record_data.get("history"),
                        encoding=record_data.get("encoding"),
                        cookies=record_data.get("cookies"),
                        elapsed=record_data.get("elapsed"),
                        request_time_sec=record_data.get("request_time_sec"),
                        request_method=record_data.get("request_method"),
                        request_url=record_data.get("request_url"),
                        request_body=record_data.get("request_body"),
                        start_time=record_data.get("start_time"),
                        end_time=record_data.get("end_time"),
                    )
                ]
            )
        failure = ""
        if len(test_record.error_record_list) == 0:
            pass
        else:
            for record_data in test_record.error_record_list:
                failure = "".join(
                    [
                        failure,
                        failure_table.format(
                            http_method=record_data[0].get("http_method"),
                            test_url=record_data[0].get("test_url"),
                            soap=record_data[0].get("soap"),
                            record_request_info=record_data[0].get("record_request_info"),
                            clean_record=record_data[0].get("clean_record"),
                            result_check_dict=record_data[0].get("result_check_dict"),
                            error=record_data[1]
                        )
                    ]
                )
        try:
            lock.acquire()
            with open(html_name + ".html", "w+") as file_to_write:
                file_to_write.write(
                    html_string.format(success_table=success, failure_table=failure)
                )
        except Exception as error:
            print(repr(error), file=sys.stderr)
        finally:
            lock.release()
