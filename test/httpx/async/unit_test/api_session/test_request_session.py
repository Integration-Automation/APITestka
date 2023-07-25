import asyncio
import sys

from je_api_testka import test_api_method_httpx_async


async def main():
    test_response = await test_api_method_httpx_async("session_get", "http://httpbin.org/get")
    if test_response is not None:
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
    try:
        test_response = await test_api_method_httpx_async("session_get", "dawdwadaw")
    except Exception as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = await test_api_method_httpx_async("http://httpbin.org/get", "session_get")
    except Exception as error:
        print(repr(error), file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
