import asyncio
import sys

from je_api_testka import test_api_method_httpx_async


async def main():
    test_response = await test_api_method_httpx_async("get", "http://httpbin.org/get")
    if test_response is not None:
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
        print(test_response.get("response_data").get("headers"))
        print(test_response.get("response_data").get("content"))
        print(test_response.get("response_data").get("history"))
        print(test_response.get("response_data").get("encoding"))
        print(test_response.get("response_data").get("cookies"))
        print(test_response.get("response_data").get("elapsed"))
        print(test_response.get("response_data").get("request_method"))
        print(test_response.get("response_data").get("request_url"))
        print(test_response.get("response_data").get("request_body"))
    test_response = await test_api_method_httpx_async("get", "http://httpbin.org/get")
    if test_response is not None:
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("json_data"))
    try:
        test_response = await test_api_method_httpx_async("get", "dawdwadaw")
    except Exception as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = await test_api_method_httpx_async("http://httpbin.org/get", "get")
    except Exception as error:
        print(repr(error), file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
