import time
from yumcache import cachedresponse


class LiveResponse:
    def __init__(self, connection, downloader, range):
        self._connection = connection
        self._downloader = downloader
        self._range = range
        self._chunked = False

    def replay(self):
        if not self._waitToStart():
            return
        self._sendHeader()
        self._sendContent()

    def _waitToStart(self):
        while self._downloader.length() is None:
            time.sleep(0.1)
            if self._downloader.error() is not None:
                cachedresponse.CachedResponse(self._connection).respondNotFound()
                return False
        return True

    def _sendHeader(self):
        if self._range is None:
            self._connection.sendall("HTTP/1.1 200 OK\r\n")
            self._connection.sendall('content-type: application/octet-stream\r\n')
            if self._downloader.length() != self._downloader.INVALID_LENGTH:
                self._connection.sendall('content-length: %d\r\n\r\n' % self._downloader.length())
                self._range = (0, self._downloader.length() - 1)
            else:
                self._chunked = True
                self._connection.sendall('Transfer-Encoding: chunked\r\n\r\n')
                self._range = (0, 1024 * 1024 * 1024)
        else:
            self._connection.sendall("HTTP/1.1 206 Partial Content\r\n")
            self._connection.sendall('content-type: application/octet-stream\r\n')
            if self._downloader.length() != self._downloader.INVALID_LENGTH:
                self._connection.sendall(
                    'content-range: bytes %d-%d/%d\r\n' % (
                        self._range[0], self._range[1], self._downloader.length()))
            else:
                self._connection.sendall(
                    'content-range: bytes %d-%d\r\n' % (self._range[0], self._range[1]))
            self._connection.sendall(
                'content-length: %d\r\n\r\n' % (self._range[1] - self._range[0] + 1))

    def _sendContent(self):
        while self._range[0] <= self._range[1]:
            before = time.time()
            segment = None
            while time.time() - before < 40:
                try:
                    segment = self._downloader.content().substr(self._range[0], self._range[1] + 1)
                except:
                    time.sleep(0.05)
                    continue
                if self._downloader.done():
                    self._range = (self._range[0], self._downloader.content().length() - 1)
                    break
                elif len(segment) == 0:
                    time.sleep(0.05)
                else:
                    break
            if segment is None:
                raise Exception("Timeout waiting for download")
            if self._chunked:
                if len(segment) > 0:
                    self._connection.sendall("%x\r\n%s\r\n" % (len(segment), segment))
            else:
                self._connection.sendall(segment)
            self._range = (self._range[0] + len(segment), self._range[1])
        if self._chunked:
            self._connection.sendall("0\r\n\r\n")
