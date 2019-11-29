from typing import Any
import sys
import time
import io
import os

class Logger2():
    def __init__(self, file1: Any, file2: Any):
        self.file1 = file1
        self.file2 = file2

    def write(self, data: str) -> None:
        self.file1.write(data)
        self.file2.write(data)

    def flush(self) -> None:
        self.file1.flush()
        self.file2.flush()


class ConsoleCapture():
    def __init__(self):
        self._stdout = None
        self._stderr = None
        self._time_start = None
        self._time_stop = None
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

    def __enter__(self):
        self._start_capturing()
        return self

    def __exit__(self, type, value, traceback):
        self._stop_capturing()

    def _start_capturing(self) -> None:
        self._time_start = time.time()
        self._stdout = io.StringIO()
        self._stderr = io.StringIO()
        sys.stdout = Logger2(self._stdout, self._original_stdout)
        sys.stderr = Logger2(self._stderr, self._original_stderr)

    def _stop_capturing(self) -> None:
        self._time_stop = time.time()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

    def runtime_info(self) -> dict:
        assert self._time_start is not None
        return dict(
            start_time=self._time_start - 0,
            end_time=self._time_stop - 0,
            stdout=self._stdout.getvalue(),
            stderr=self._stderr.getvalue()
        )
