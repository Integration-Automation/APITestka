==================
APITestka Argument Doc
==================

.. code-block:: python

        """
        status_code: response status code
        text: response text
        content: response content
        headers: response headers
        history: response history
        encoding: response encoding
        cookies: response cookies
        elapsed: response encoding
        request_time_sec: request time
        request_url: request url
        request_url: response body
        start_time: request start time
        end_time: request end time
        """
        response_data = {
            "status_code": response.status_code,
            "text": response.text,
            "content": response.content,
            "headers": response.headers,
            "history": response.history,
            "encoding": response.encoding,
            "cookies": dict_from_cookiejar(response.cookies),
            "elapsed": response.elapsed,
            "request_time_sec": response.elapsed.total_seconds(),
            "request_method": response.request.method,
            "request_url": response.request.url,
            "request_body": response.request.body,
            "start_time": start_time,
            "end_time": end_time
        }

