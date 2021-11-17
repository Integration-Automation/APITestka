from json import dumps


def __process_json(json_string: str, **kwargs):
    return dumps(json_string, **kwargs)


def reformat_json(json_string: str):
    return __process_json(json_string, indent=4, sort_keys=True)

