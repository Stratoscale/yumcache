import tempfile
import subprocess
import shutil
import time
import socket

PORT = 10701


class YumCacheWrapper:
    def __init__(self):
        self._dir = tempfile.mkdtemp()
        self._popen = subprocess.Popen(
            ["python", "yumcache/main.py", "--storage=" + self._dir, "--port=" + str(PORT)],
            close_fds=True)
        self._waitToComeOnline()

    def _waitToComeOnline(self):
        while True:
            sock = socket.socket()
            try:
                sock.connect(("localhost", PORT))
                break
            except:
                pass
            finally:
                sock.close()
            time.sleep(0.05)

    def directory(self):
        return self._dir

    def done(self):
        self._popen.terminate()
        self._popen.wait()
        shutil.rmtree(self._dir, ignore_errors=True)
