"""The ``APITestka`` logger, the file it writes to, and the handler that feeds the GUI.

The log file is ``~/.je_api_testka/logs/APITestka.log`` unless ``APITESTKA_LOG_FILE`` names another
path (a relative one resolves against the cwd at import time; ``os.devnull`` turns the file off). It
used to be ``APITestka.log`` in the working directory, opened for overwrite at import with the
locale encoding, so every process that imported the package -- TestPioneer, PyBreeze, the pytest
plugin -- left a file wherever it started and wiped the previous run's log.

The file is opened on the first record, so importing writes nothing. It is shared by every process
on the account, so it is appended to, each line carries the process id, and it is rotated only when
a process opens it (Windows cannot rename a file another process holds open).
"""
import logging
import os
import warnings
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from je_api_testka.gui.message_queue import api_testka_ui_queue

#: Environment variable that overrides where the log file is written.
LOG_FILE_ENV = "APITESTKA_LOG_FILE"

#: A file past this size is moved to ``<name>.1`` when a process opens it.
ROTATE_AT_BYTES = 10 * 1024 * 1024

apitestka_logger = logging.getLogger("APITestka")
# Only this logger's level is ours to set. The root logger used to be forced to DEBUG here, which
# imposed DEBUG on every application that imported APITestka and every library it uses.
apitestka_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(process)d | %(name)s | %(levelname)s | %(message)s')


def default_log_file() -> Path:
    """Return the log file path: ``$APITESTKA_LOG_FILE``, else the home-directory default."""
    configured = os.environ.get(LOG_FILE_ENV, "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".je_api_testka" / "logs" / "APITestka.log"


def _rotate_if_large(path: Path, limit: int) -> None:
    """Move ``path`` to ``<path>.1`` past ``limit`` bytes; best effort while another process holds it."""
    try:
        if limit <= 0 or not path.is_file() or path.stat().st_size <= limit:
            return
        os.replace(path, path.with_name(path.name + ".1"))
    except OSError:
        return


class APITestkaLoggingHandler(RotatingFileHandler):
    """Append-mode UTF-8 file handler; a file that cannot be opened becomes ``os.devnull`` with one warning."""

    def __init__(self, filename: Optional[str] = None, delay: bool = True) -> None:
        path = filename if filename is not None else str(default_log_file())
        super().__init__(filename=path, mode="a", encoding="utf-8",
                         errors="backslashreplace", delay=delay)
        self.setFormatter(formatter)
        self.setLevel(logging.DEBUG)

    def _open(self):
        path = Path(self.baseFilename)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            _rotate_if_large(path, ROTATE_AT_BYTES)
            return super()._open()
        except OSError as error:
            warnings.warn(f"APITestka log file {path} unavailable, file logging off: {error!r}",
                          RuntimeWarning, stacklevel=2)
            return open(os.devnull, self.mode, encoding=self.encoding, errors=self.errors)  # noqa: SIM115


class QueueLogHandler(logging.Handler):
    """
    自訂 Logger Handler，把訊息丟到 UI 佇列
    Custom logger handler that pushes log records into UI queue
    """

    def emit(self, record: logging.LogRecord):
        log_entry = self.format(record)
        api_testka_ui_queue.put(log_entry)


# File handler, opened on the first record
file_handler = APITestkaLoggingHandler()
queue_log_handler = QueueLogHandler()
apitestka_logger.addHandler(queue_log_handler)
apitestka_logger.addHandler(file_handler)
