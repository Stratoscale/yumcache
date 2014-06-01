class CachedResponse:
    def __init__(self, connection):
        self._connection = connection

    def respond(self, content, range):
        if range is None:
            self._connection.sendall("HTTP/1.1 200 OK\r\n")
            self._connection.sendall('content-type: application/octet-stream\r\n')
            self._connection.sendall('content-length: %d\r\n\r\n' % len(content))
            self._connection.sendall(content)
        else:
            self._connection.sendall("HTTP/1.1 206 Partial Content\r\n")
            self._connection.sendall('content-type: application/octet-stream\r\n')
            self._connection.sendall('content-range: bytes %d-%d/%d\r\n' % (
                range[0], range[1], len(content)))
            self._connection.sendall('content-length: %d\r\n\r\n' % (range[1] - range[0] + 1))
            self._connection.sendall(content[range[0]: range[1] + 1])

    def respondNotFound(self):
        self._connection.sendall("HTTP/1.1 404 NOT FOUND\r\n\r\n")
