import asyncio
import sys

from je_api_testka import test_api_method_httpx_async

async def main():
    test_response = await test_api_method_httpx_async("options", "http://httpbin.org/get")
    if test_response is not None:
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("elapsed"))
    try:
        test_response = await test_api_method_httpx_async("options", "dawdwadaw")
    except Exception as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = await test_api_method_httpx_async("http://httpbin.org/get", "options")
    except Exception as error:
        print(repr(error), file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
