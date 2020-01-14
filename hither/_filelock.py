import sys
_win32 = (sys.platform == 'win32')
if _win32:
    import portalocker
else:
    import fcntl
import errno
import time
import random
from typing import IO, Optional


class FileLock():
    def __init__(self, path: str, exclusive: bool=True, _disable_lock: bool=False):
        """Lock a file using an exclusive or non-exclusive lock.
        
        Modified by James Jun on 2020/1/13. fcntl is replaced by portalocker when in windows

        Example usage:
        ```
        with FileLock('some_file.txt.lock', exclusive=True):
            # Do something with some_file.txt
        ```
        
        Rather than locking a file directly, it is helpful to lock an adjacent
        .lock file.

        Exclusive locks are useful for read/write access whereas non-exclusive
        locks are useful for readonly access.

        Parameters
        ----------
        path : str
            Path to the file to lock
        exclusive : bool, optional
            Whether the lock should be exclusive, by default True
        _disable_lock : bool, optional
            For testing purposes, do not actually lock, by default False
        """
        self._path = path
        self._file: Optional[IO] = None
        self._disable_lock = _disable_lock
        self._exclusive = exclusive

    def __enter__(self) -> None:
        if self._disable_lock:
            return
        self._file = open(self._path, 'w+')
        num_tries = 0
        while True:
            try:
                if self._exclusive:
                    if _win32:
                        portalocker.lock(self._file, portalocker.LOCK_EX | portalocker.LOCK_NB)
                    else:
                        fcntl.flock(self._file, fcntl.LOCK_EX | fcntl.LOCK_NB)                    
                else:
                    if _win32:
                        portalocker.lock(self._file, portalocker.LOCK_SH | portalocker.LOCK_NB)
                    else:
                        fcntl.flock(self._file, fcntl.LOCK_SH | fcntl.LOCK_NB)                    
                if num_tries > 10:
                    print('Locked file {} after {} tries (exclusive={})...'.format(self._path, num_tries, self._exclusive))
                break
            except IOError as e:
                if e.errno != errno.EAGAIN:
                    raise
                else:
                    num_tries = num_tries + 1
                    time.sleep(random.uniform(0, 0.1))

    def __exit__(self, type, value: object, traceback) -> None:
        if self._disable_lock:
            return
        if self._file is not None:
            if _win32:
                portalocker.unlock(self._file)
            else:
                fcntl.flock(self._file, fcntl.LOCK_UN)            
            self._file.close()
