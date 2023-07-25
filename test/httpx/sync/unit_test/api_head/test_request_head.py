import sys

from je_api_testka import test_api_method_httpx

if __name__ == "__main__":
    import requests

    test_response = test_api_method_httpx("head", "http://httpbin.org/get", headers={
        'x-requested-with': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    })
    if test_response is not None:
        print(test_response.get("response_data"))
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("elapsed"))
    try:
        test_response = test_api_method_httpx("head", "dawdwadaw")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = test_api_method_httpx("http://httpbin.org/get", "head")
    except Exception as error:
        print(repr(error), file=sys.stderr)
