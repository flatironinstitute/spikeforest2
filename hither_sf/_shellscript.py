import subprocess
import sys
import tempfile
import shutil
import signal
import os
import time
import io
from typing import Optional, List, Any
from ._preventkeyboardinterrupt import PreventKeyboardInterrupt

class ShellScript():
    def __init__(self, script: str, script_path: Optional[str]=None, keep_temp_files: bool=False, verbose: bool=False, label='', docker_container_name=None, redirect_output_to_stdout=False):
        self._script_path = script_path
        self._keep_temp_files = keep_temp_files
        self._process: Optional[subprocess.Popen] = None
        self._files_to_remove: List[str] = []
        self._dirs_to_remove: List[str] = []
        self._start_time: Optional[float] = None
        self._verbose = verbose
        self._label = label
        self._docker_container_name = docker_container_name
        self._redirect_output_to_stdout = redirect_output_to_stdout

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

    def substitute(self, old: str, new: Any) -> None:
        self._script = self._script.replace(old, '{}'.format(new))

    def write(self, script_path: Optional[str]=None) -> None:
        if script_path is None:
            script_path = self._script_path
        if script_path is None:
            raise Exception('Cannot write script. No path specified')
        with open(script_path, 'w', newline='\n') as f:
            f.write(self._script)
        os.chmod(script_path, 0o744)

    def start(self) -> None:
        if self._script_path is not None:
            script_path = self._script_path
        else:
            tempdir = tempfile.mkdtemp(prefix='tmp_shellscript_')
            if (sys.platform == "win32"):
                script_path = os.path.join(tempdir, 'script.bat')
            else:
                script_path = os.path.join(tempdir, 'script.sh')
            self._dirs_to_remove.append(tempdir)        
        self.write(script_path)
        cmd = script_path
        if self._verbose:
            print('RUNNING SHELL SCRIPT: ' + cmd)
        self._start_time = time.time()
        if self._redirect_output_to_stdout:
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            self._process = subprocess.Popen(cmd)

    def wait(self, timeout=None) -> Optional[int]:
        timeout_increment = 0.01
        if timeout is None or (timeout > timeout_increment):
            timer = time.time()
            while True:
                retcode = self.wait(timeout=timeout_increment)
                if retcode is not None:
                    return retcode
                if timeout is not None:
                    elapsed = time.time() - timer
                    if elapsed > timeout:
                        return None

        if not self.isRunning():
            self._print_stdout()
            return self.returnCode()
        assert self._process is not None, "Unexpected self._process is None even though it is running."
        try:
            retcode = self._process.wait(timeout=timeout)
            self._cleanup()
            self._print_stdout()
            return retcode
        except:
            self._print_stdout()
            return None
    
    def _print_stdout(self):
        if not self._redirect_output_to_stdout:
            return
        if self._process is None:
            return
        for line in self._process.stdout:
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            print(line)

    def _cleanup(self) -> None:
        try:
            if not hasattr(self, '_dirs_to_remove'):
                return
            if self._keep_temp_files:
                return
            for dirpath in self._dirs_to_remove:
                _rmdir_with_retries(dirpath, num_retries=5)
        except:
            print('WARNING: Problem in cleanup() of ShellScript')

    def stop(self) -> None:
        with PreventKeyboardInterrupt():
            if not self.isRunning():
                return
            assert self._process is not None, "Unexpected self._process is None even though it is running."

            self._cleanup()

            signals = [signal.SIGINT, signal.SIGINT, signal.SIGINT] + [signal.SIGTERM, signal.SIGTERM, signal.SIGTERM] + [signal.SIGKILL]
            signal_strings = ['SIGINT', 'SIGINT', 'SIGINT'] + ['SIGTERM', 'SIGTERM', 'SIGTERM'] + ['SIGKILL']
            delays = [5, 5, 5] + [5, 5, 5] + [1]

            for iis in range(len(signals)):
                if self._docker_container_name is None:
                    self._process.send_signal(signals[iis])
                else:
                    self._send_docker_signal(signal_strings[iis])
                try:
                    self._process.wait(timeout=delays[iis])
                    return
                except:
                    pass
    
    def _send_docker_signal(self, sig_str):
        cmd = f'docker kill {self._docker_container_name} -s {sig_str}'
        print(cmd)
        os.system(cmd)

    def kill(self) -> None:
        if not self.isRunning():
            return
        
        assert self._process is not None, "Unexpected self._process is None even though it is running."
        if self._docker_container_name is None:
            self._process.send_signal(signal.SIGKILL)
        else:
            self._send_docker_signal('SIGKILL')
        try:
            self._process.wait(timeout=1)
        except:
            print('WARNING: unable to kill shell script.')
            pass

    def stopWithSignal(self, sig, timeout) -> bool:
        if not self.isRunning():
            return True
        
        assert self._process is not None, "Unexpected self._process is None even though it is running."
        if self._docker_container_name is None:
            self._process.send_signal(sig)
        else:
            if sig == signal.SIGINT:
                sig_str = 'SIGINT'
            elif sig == signal.SIGTERM:
                sig_str = 'SIGTERM'
            elif sig == signal.SIGKILL:
                sig_str = 'SIGKILL'
            else:
                raise Exception(f'Unable to determine signal string for signal {sig}')
            self._send_docker_signal(sig_str)
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
