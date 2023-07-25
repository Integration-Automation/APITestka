import asyncio
import sys

import requests.exceptions

from je_api_testka import generate_html
from je_api_testka import test_api_method_httpx_async
from je_api_testka.httpx_wrapper.async_httpx_method import delegate_async_httpx


async def main():
    test_response = await test_api_method_httpx_async("delete", "http://httpbin.org/delete")
    if test_response is not None:
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
        print(test_response.get("response_data").get("elapsed"))
        print(test_response.get("response_data").get("elapsed").total_seconds())
        print(test_response.get("response_data").get("request_time_sec"))
    try:
        test_response = await test_api_method_httpx_async("delete", "wadwaddawdwa")
    except requests.exceptions.MissingSchema as error:
        print(repr(error), file=sys.stderr)
    try:
        test_response = await test_api_method_httpx_async("dwadadwawd", "delete")
    except Exception as error:
        print(repr(error), file=sys.stderr)

    generate_html()


if __name__ == "__main__":
    asyncio.run(main())
