from twisted.web.server import Site
from twisted.internet import reactor
from twisted.web.static import File
import sys
import tempfile
import subprocess
import shutil
import time
import socket

PORT = 10700


class FakeServer:
    def __init__(self):
        self._dir = tempfile.mkdtemp()
        self._popen = subprocess.Popen(["python", __file__, self._dir], close_fds=True)
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


def server():
    root = File(sys.argv[1])
    factory = Site(root)
    reactor.listenTCP(PORT, factory)
    reactor.run()


if __name__ == "__main__":
    server()
