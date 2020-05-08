from typing import Any, Dict, Union
import sys
import time
import io

class CustomStdout():
    def __init__(self, label, console_out, original_stdout, stderr=False, show_console=True):
        self._label = label
        self._console_out = console_out
        self._original_stdout = original_stdout
        self._stderr = False
        self._show_console = show_console

    def write(self, data: str) -> None:
        lines = data.splitlines(keepends=False)
        for line in lines:
            if line:
                a: Dict[Union[float, str, bool]] = dict(
                    timestamp=time.time() - 0,
                    text=line
                )
                if self._stderr:
                    a['stderr'] = True
                self._console_out['lines'].append(a)
                if self._show_console:
                    print('{} {}: {}'.format(self._label, _fmt_time(a['timestamp']), a['text']), file=self._original_stdout)
        
    def flush(self) -> None:
        pass

def _fmt_time(t):
    import datetime
    return datetime.datetime.fromtimestamp(t).isoformat()

class ConsoleCapture():
    def __init__(self, label='', show_console=True):
        self._label = label
        self._console_out = dict(label=label, lines=[])
        self._time_start = None
        self._time_stop = None
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._show_console = show_console

    def __enter__(self):
        self._start_capturing()
        return self

    def __exit__(self, type, value, traceback):
        self._stop_capturing()

    def _start_capturing(self) -> None:
        self._time_start = time.time()
        sys.stdout = CustomStdout(self._label, self._console_out, self._original_stdout, show_console=self._show_console)
        sys.stderr = CustomStdout(self._label, self._console_out, self._original_stderr, stderr=True, show_console=self._show_console)

    def _stop_capturing(self) -> None:
        self._time_stop = time.time()
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

    def runtime_info(self) -> dict:
        assert self._time_start is not None
        return dict(
            start_time=self._time_start - 0,
            end_time=self._time_stop - 0,
            elapsed_sec = self._time_stop - self._time_start,
            console_out=self._console_out
        )