import json
import os

import pytest

from je_api_testka import read_action_json, reformat_json, write_action_json


def test_reformat_valid_json_string():
    """Reformat a valid JSON string."""
    test_json_string = '[["get", "https://httpbin.org/get"]]'
    result = reformat_json(test_json_string)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed == [["get", "https://httpbin.org/get"]]


def test_reformat_invalid_json_raises():
    """Reformatting invalid JSON should raise JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        reformat_json("not_valid_json_at_all")


def test_reformat_invalid_json_braces_raises():
    """Reformatting malformed JSON with braces should raise."""
    with pytest.raises(json.JSONDecodeError):
        reformat_json("{90}{DW]dadw[dladwkadodkawokdwadwadaw}")


def test_write_and_read_action_json(tmp_path):
    """Write a JSON action list and read it back."""
    test_list = [
        ["AT_test_api_method", {
            "http_method": "get", "test_url": "https://httpbin.org/get",
        }],
        ["AT_test_api_method", {
            "http_method": "post", "test_url": "https://httpbin.org/post",
            "params": {"task": "new task"},
        }],
    ]
    json_path = str(tmp_path / "test_action.json")
    write_action_json(json_path, test_list)
    assert os.path.exists(json_path)

    read_data = read_action_json(json_path)
    assert read_data == test_list


def test_reformat_read_json(tmp_path):
    """Write, read, and reformat a JSON file."""
    test_list = [["AT_test_api_method", {"http_method": "get", "test_url": "https://httpbin.org/get"}]]
    json_path = str(tmp_path / "test_reformat.json")
    write_action_json(json_path, test_list)

    read_data = read_action_json(json_path)
    reformatted = reformat_json(read_data)
    assert isinstance(reformatted, str)
