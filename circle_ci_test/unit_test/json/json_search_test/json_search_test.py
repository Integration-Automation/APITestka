import sys

if __name__ == "__main__":
    from je_api_testka import reformat_json
    from je_api_testka import json_element_find
    from je_api_testka import APITesterJsonException

    test_json = [
        {
            "get1": ("get", "http://httpbin.org/get", False, {"headers": {
                'x-requested-with': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
            }}),
            "post1": ("post", "http://httpbin.org/post", False, {"params": {"task": "new task"}})
        }
    ]
    new_test_json = reformat_json(test_json)
    print(new_test_json)
    print(json_element_find(new_test_json, "post1"))
    test_json = {
        "test": "test_data"
    }
    print(json_element_find(test_json, "test"))
    test_json = {
        list: (),
        "test": "test_data"
    }
    print(json_element_find(test_json, list))
    print(json_element_find(test_json, "test"))
    test_json = {
        "a": {},
        "test": "test_data"
    }
    print(json_element_find(test_json, "a"))
    print(json_element_find(test_json, "test"))
    test_json = {
        "a": str(list(["a", "b", "c"])),
        "test": list
    }
    print(json_element_find(test_json, "a"))
    print(json_element_find(test_json, "test"))
    test_json = [{
        "a": str(list(["a", "b", "c"])),
        "test": list
    }]
    print(json_element_find(test_json, "a"))
    print(json_element_find(test_json, "test"))
    try:
        test_json = {
            ("a", "b", "c")
        }
        print(json_element_find(test_json, "a"))
        print(json_element_find(test_json, "test"))
    except APITesterJsonException as error:
        print(error.__str__(), sep="\n", file=sys.stderr)
    try:
        test_json = {
            "b": ("a", "b", "c")
        }
        print(json_element_find(test_json, "a"))
    except APITesterJsonException as error:
        print(str(error), sep="\n", file=sys.stderr)
    try:
        test_json = {
            "c": ("a", "b", "c", ("aaa", "ddd"))
        }
        print(json_element_find(test_json, "a"))
    except APITesterJsonException as error:
        print(repr(error), file=sys.stderr)
        