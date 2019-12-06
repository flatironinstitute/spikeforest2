import sys
import time
import io
import os
import subprocess
import tempfile
import shutil
import signal
from typing import Optional, List, Any


def main():
    script = ShellScript('''
    #!/bin/bash

    echo "hello 1"
    sleep 3
    docker run hello-world
    sleep 3
    echo "hello 2"
    ''')
    with ConsoleCapture() as cc:
        print('abc')
        script.start()
        script.wait()
        sys.stderr.write('test')
    
    runtime_info = cc.runtime_info()
    print(runtime_info)
    print(runtime_info['console_out'])

class Logger3():
    def __init__(self, file1: Any, file2: Any, file3: Any):
        self.file1 = file1
        self.file2 = file2
        self.file3 = file3

    def write(self, data: str) -> None:
        self.file1.write(data)
        self.file2.write(data)
        self.file3.write(data)

    def flush(self) -> None:
        self.file1.flush()
        self.file2.flush()
        self.file3.flush()
    
    def fileno(self) -> int:
        return -1


class ConsoleCapture():
    def __init__(self):
        self._stdout = None
        self._stderr = None
        self._console_out = None
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
        self._console_out = io.StringIO()
        sys.stdout = Logger3(self._stdout, self._console_out, self._original_stdout)
        sys.stderr = Logger3(self._stderr, self._console_out, self._original_stderr)

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
            stdout=self._stdout.getvalue(),
            stderr=self._stderr.getvalue(),
            console_out=self._console_out.getvalue()
        )

class ShellScript():
    def __init__(self, script: str, script_path: Optional[str]=None, keep_temp_files: bool=False, verbose: bool=False):
        lines = script.splitlines()
        lines = self._remove_initial_blank_lines(lines)
        if len(lines) > 0:
            num_initial_spaces = self._get_num_initial_spaces(lines[0])
            for ii, line in enumerate(lines):
                if len(line.strip()) > 0:
                    n = self._get_num_initial_spaces(line)
                    if n < num_initial_spaces:
                        print(script)
                        raise Exception('Problem in script. First line must not be indented relative to others')
                    lines[ii] = lines[ii][num_initial_spaces:]
        self._script = '\n'.join(lines)
        self._script_path = script_path
        self._keep_temp_files = keep_temp_files
        self._process: Optional[subprocess.Popen] = None
        self._files_to_remove: List[str] = []
        self._dirs_to_remove: List[str] = []
        self._start_time: Optional[float] = None
        self._verbose = verbose

    def __del__(self):
        self.cleanup()

    def substitute(self, old: str, new: Any) -> None:
        self._script = self._script.replace(old, '{}'.format(new))

    def write(self, script_path: Optional[str]=None) -> None:
        if script_path is None:
            script_path = self._script_path
        if script_path is None:
            raise Exception('Cannot write script. No path specified')
        with open(script_path, 'w') as f:
            f.write(self._script)
        os.chmod(script_path, 0o744)

    def start(self) -> None:
        print('start 1')
        print('start 2')
        if self._script_path is not None:
            script_path = self._script_path
        else:
            tempdir = tempfile.mkdtemp(prefix='tmp_shellscript_')
            script_path = os.path.join(tempdir, 'script.sh')
            self._dirs_to_remove.append(tempdir)
        self.write(script_path)
        cmd = script_path
        if self._verbose:
            print('RUNNING SHELL SCRIPT: ' + cmd)
        self._start_time = time.time()
        stdout_fname = tempdir + '/stdout.txt'
        stderr_fname = tempdir + '/stderr.txt'
        with open(stdout_fname, 'w') as f:
            pass
        with open(stderr_fname, 'w') as f:
            pass
        print('start 3')
        self._stdout_file = open(stdout_fname, 'r')
        self._stderr_file = open(stderr_fname, 'r')
        self._process = subprocess.Popen(cmd + f' >> {tempdir}/stdout.txt 2>> {tempdir}/stderr.txt', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('start 4')

    def wait(self, timeout=None) -> Optional[int]:
        timer = time.time()
        if not self.isRunning():
            return self.returnCode()
        assert self._process is not None, "Unexpected self._process is None even though it is running."
        print('wait A')
        print('wait B')
        while True:
            print('wait C')
            print('wait D')
            retcode = self._process.poll()
            
            print('wait E')
            print('wait F')

            lines = self._stdout_file.readlines()
            for line in lines:
                if isinstance(line, bytes): line = line.decode('utf-8')
                print('{}'.format(line))

            lines = self._stderr_file.readlines()
            for line in lines:
                print('{}'.format(line))

            if retcode is not None:
                self._stdout_file.close()
                self._stderr_file.close()
                return retcode
            elapsed = time.time() - timer
            if timeout is not None:
                if elapsed > timeout:
                    return None
            time.sleep(0.1)

    def cleanup(self) -> None:
        if self._keep_temp_files:
            return
        for dirpath in self._dirs_to_remove:
            _rmdir_with_retries(dirpath, num_retries=5)

    def stop(self) -> None:
        if not self.isRunning():
            return
        assert self._process is not None, "Unexpected self._process is None even though it is running."

        signals = [signal.SIGINT] * 10 + [signal.SIGTERM] * 10 + [signal.SIGKILL] * 10

        for signal0 in signals:
            self._process.send_signal(signal0)
            try:
                self._process.wait(timeout=0.02)
                return
            except:
                pass

    def kill(self) -> None:
        if not self.isRunning():
            return
        
        assert self._process is not None, "Unexpected self._process is None even though it is running."
        self._process.send_signal(signal.SIGKILL)
        try:
            self._process.wait(timeout=1)
        except:
            print('WARNING: unable to kill shell script.')
            pass

    def stopWithSignal(self, sig, timeout) -> bool:
        if not self.isRunning():
            return True
        
        assert self._process is not None, "Unexpected self._process is None even though it is running."
        self._process.send_signal(sig)
        try:
            self._process.wait(timeout=timeout)
            return True
        except:
            return False

    def elapsedTimeSinceStart(self) -> Optional[float]:
        if self._start_time is None:
            return None
        
        return time.time() - self._start_time

    def isRunning(self) -> bool:
        if not self._process:
            return False
        retcode = self._process.poll()
        if retcode is None:
            return True
        return False

    def isFinished(self) -> bool:
        if not self._process:
            return False
        return not self.isRunning()

    def returnCode(self) -> Optional[int]:
        if not self.isFinished():
            raise Exception('Cannot get return code before process is finished.')
        assert self._process is not None, "Unexpected self._process is None even though it is finished."
        return self._process.returncode

    def scriptPath(self) -> Optional[str]:
        return self._script_path

    def _remove_initial_blank_lines(self, lines: List[str]) -> List[str]:
        ii = 0
        while ii < len(lines) and len(lines[ii].strip()) == 0:
            ii = ii + 1
        return lines[ii:]

    def _get_num_initial_spaces(self, line: str) -> int:
        ii = 0
        while ii < len(line) and line[ii] == ' ':
            ii = ii + 1
        return ii


def _rmdir_with_retries(dirname, num_retries, delay_between_tries=1):
    for retry_num in range(1, num_retries + 1):
        if not os.path.exists(dirname):
            return
        try:
            shutil.rmtree(dirname)
            break
        except:
            if retry_num < num_retries:
                print('Retrying to remove directory: {}'.format(dirname))
                time.sleep(delay_between_tries)
            else:
                raise Exception('Unable to remove directory after {} tries: {}'.format(num_retries, dirname))

if __name__ == '__main__':
    main()