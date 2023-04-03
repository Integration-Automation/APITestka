import sys

import requests.exceptions

from je_api_testka import test_api_method

if __name__ == "__main__":
    login_url = "https://phpzag.com/demo/ajax_login_script_with_php_jquery/login.php"
    welcome_url = "https://phpzag.com/demo/ajax_login_script_with_php_jquery/welcome.php"

    payload = 'user_email=test@phpzag.com&password=test&login_button='
    login_headers = {
        'x-requested-with': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    }
    test_response_post = test_api_method("session_post", login_url, headers=login_headers, data=payload)
    if test_response_post is not None:
        print(test_response_post.get("response_data").get("status_code"))
        print(test_response_post.get("response_data").get("text"))
        test_response_get = test_api_method("session_get", welcome_url, headers=login_headers)
        print(test_response_get.get("response_data").get("status_code"))
        print(test_response_get.get("response_data").get("text"))

    try:
        test_response_get = test_api_method("dwadwadadw", "dwadawdwdadw", headers={"aa": "ttawtwafaw"})
    except Exception as error:
        print(repr(error), file=sys.stderr)
    try:
        new_test_response_get = test_api_method("get", "dwadawdwdadw", headers={"aa": "ttawtwafaw"})
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)
