import asyncio
import sys

from je_api_testka import test_api_method_httpx_async


async def main():
    test_response = await test_api_method_httpx_async("get", "http://httpbin.org/get",
                                                      result_check_dict={"status_code": "200"})
    if test_response is not None:
        print(test_response.get("response_data").get("status_code"))

    # will raise exception because result_check_dict status_code not 300
    try:
        test_response = await test_api_method_httpx_async("get", "http://httpbin.org/get",
                                                          result_check_dict={"status_code": "300"})
    except Exception as error:
        print(repr(error), file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
