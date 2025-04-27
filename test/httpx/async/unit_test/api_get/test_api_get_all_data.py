import asyncio

from je_api_testka import test_api_method_httpx_async


async def main():
    import sys

    sys.stdout.reconfigure(encoding='utf-8')
    test_response = await test_api_method_httpx_async("get", "http://httpbin.org")

    if test_response is not None:
        print(test_response)
        print(test_response.get("response_data"))
    try:
        test_response = await test_api_method_httpx_async("get", "wadwaddawdwa")
    except Exception as error:
        print(repr(error), file=sys.stderr)

    try:
        test_response = await test_api_method_httpx_async("dwadadwawd", "get")
    except Exception as error:
        print(repr(error), file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())