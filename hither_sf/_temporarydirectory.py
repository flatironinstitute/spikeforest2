import os
import shutil
import tempfile
import time


class TemporaryDirectory():
    def __init__(self, remove=True, prefix='tmp'):
        self._remove = remove
        self._prefix = prefix

    def __enter__(self) -> str:
        storage_dir = os.environ.get('KACHERY_STORAGE_DIR', None)
        if storage_dir:
            dirpath = os.path.join(storage_dir, 'tmp')
            if not os.path.exists(dirpath):
                os.mkdir(dirpath)
        else:
            dirpath = None
        self._path = str(tempfile.mkdtemp(prefix=self._prefix, dir=dirpath))
        return self._path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._remove:
            _rmdir_with_retries(self._path, num_retries=5)

    def path(self):
        return self._path


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
