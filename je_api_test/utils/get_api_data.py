def get_api_response_data(response):
    return {
            "status_code": response.status_code,
            "text": response.text,
            "content": response.content,
            "headers": response.headers,
            "history": response.history,
            "encoding": response.encoding,
            "cookies": response.cookies,
            "elapsed": response.elapsed
        }