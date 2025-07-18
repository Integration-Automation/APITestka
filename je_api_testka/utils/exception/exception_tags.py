# Unknown error
error_message: str = "Unknown API tester error"
wrong_http_method_error_message: str = "Invalid HTTP method"
http_method_have_wrong_type: str = "HTTP method parameter is of invalid type"

# get data error
get_data_error_message: str = "Failed to retrieve API data"

# Http Method error
get_error_message: str = "API tester GET request failed"
get_json_error_message: str = "Failed to parse JSON from GET response"
put_error_message: str = "API tester PUT request failed"
delete_error_message: str = "API tester DELETE request failed"
post_error_message: str = "API tester POST request failed"
head_error_message: str = "API tester HEAD request failed"
options_error_message: str = "API tester OPTIONS request failed"
patch_error_message: str = "API tester PATCH request failed"
session_error_message: str = "API tester session error"

# response code error
response_code_error: str = "Unexpected response code"

# response body error
response_body_error: str = "Invalid response body"

# response timeout error
response_timeout_error: str = "Request timed out"

# response history error
response_history_error: str = "Response history error"

# response encoding error
response_encoding_error: str = "Response encoding error"

# response cookies error
response_cookies_error: str = "Response cookies error"

# response headers error
response_headers_error: str = "Response headers error"

# response content error
response_content_error: str = "Response content error"

# response text error
response_text_error: str = "Response text error"

# execute action error
execute_action_error: str = "Failed to execute action"

# json error
cant_find_json_error: str = "JSON element not found"
cant_save_json_error: str = "Failed to save JSON"
cant_save_json_report_record_us_null: str = "Cannot save JSON: record is null"
cant_reformat_json_error: str = "Failed to reformat JSON: incorrect type"
cant_find_element_in_json_error: str = "Cannot find element in JSON"
json_type_error: str = "JSON type error"
wrong_json_data_error: str = "Failed to parse JSON"

# XML error
cant_read_xml_error: str = "Cannot read XML"
xml_type_error: str = "XML type error"

# Executor error
executor_data_error: str = "Executor received invalid data"
executor_list_error: str = "Executor received invalid data: list is None or wrong type"

# API data check
status_code_error: str = "Request status code error"
status_text_error: str = "Request text error"
status_content_error: str = "Request content error"
status_headers_error: str = "Request headers error"
status_history_error: str = "Request history error"
status_encoding_error: str = "Request encoding error"
status_cookies_error: str = "Request cookies error"
status_elapsed_error: str = "Request elapsed time error"
status_requests_method_error: str = "Invalid request method"
status_requests_url_error: str = "Invalid request URL"
status_requests_body_error: str = "Invalid request body"

# HTML
html_generate_no_data_tag: str = "No data for HTML generation"

# add command
add_command_exception_tag: str = "Command value must be a method or function"

# argparse
argparse_get_wrong_data: str = "Argparse received invalid data"

# Callback executor
get_bad_trigger_method: str = "Invalid trigger method: only accepts kwargs and args"
get_bad_trigger_function: str = "Invalid trigger function: only functions in event_dict are accepted"

# Mock server
get_bad_api_router_setting: str = "Invalid API router setting"