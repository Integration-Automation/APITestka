import queue
import subprocess
from threading import Thread

encoding = "utf-8"


def read_program_output_from_process():
    while True:
        program_output_data = process.stdout.raw.read(1024).decode(encoding)
        if program_output_data.strip() != "" or program_output_data.strip() != "\n":
            std_out_queue.put(program_output_data)


def read_program_error_output_from_process():
    while True:
        program_error_output_data = process.stderr.raw.read(1024).decode(encoding)
        if program_error_output_data.strip() != "" or program_error_output_data.strip() != "\n":
            std_err_queue.put(program_error_output_data)


test_list = ["python", "-m", "je_api_testka", "--execute_str",
        '{"api_testka":[["test_api_method",{ "http_method": "post", "test_url": "http://httpbin.org/post", "params": { "task": "new task" } }], ["test_api_method", { "http_method": "post", "test_url": "http://httpbin.org/post"}]]}'
             ]

std_out_queue = queue.Queue()
std_err_queue = queue.Queue()

process = subprocess.Popen(
    test_list,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

read_program_output_from_thread = Thread(
    target=read_program_output_from_process,
    daemon=True
).start()
# program error message queue thread
read_program_error_output_from_thread = Thread(
    target=read_program_error_output_from_process,
    daemon=True
).start()


while True:
    if not std_out_queue.empty():
        print(std_out_queue.get_nowait())
    if not std_err_queue.empty():
        print(std_err_queue.get_nowait())
    process.poll()
    if process.returncode is not None:
        process.terminate()
        break



