import logging
import re
import urllib


class NoMoreRequests(Exception):
    pass


class Request:
    def __init__(self, connection):
        self._connection = connection
        self._action, self._path, self._range = self._receiveRequest()

    def action(self):
        return self._action

    def path(self):
        return self._path

    def range(self):
        return self._range

    def hostname(self):
        return urllib.unquote(self._rawHostname())

    def _rawHostname(self):
        return self._path.split("/")[1]

    def pathInHost(self):
        return self._path[len("/") + len(self._rawHostname()):]

    def _receiveRequest(self):
        action, path = self._receiveRequestLine()
        headers = ""
        while True:
            line = self._receiveLine()
            headers += line
            if line.strip() == "":
                break
        match = re.search(r"\nrange:\s*bytes=(\d+)-(\d+)\r\n", "\r\n" + headers, re.IGNORECASE)
        if match is None:
            range = None
        else:
            range = int(match.group(1)), int(match.group(2))
        return action, path, range

    def _receiveRequestLine(self):
        line = self._receiveLine()
        logging.info("Received Request line %s", (line,))
        action, path = re.search(r"^(\w+) (.*) HTTP/.+$", line.strip()).groups()
        return action, path.replace("//", "/")

    def _receiveLine(self):
        line = ""
        while not line.endswith("\n"):
            data = self._connection.recv(1)
            if data == "":
                raise NoMoreRequests("No More Requests")
            line += data
        return line
