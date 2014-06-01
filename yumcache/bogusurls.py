import time
import requests


class BogusURLs:
    def __init__(self, mirrors):
        self._mirrors = mirrors
        self._selected = {}

    def replace(self, hostname, pathInHost):
        if hostname not in self._mirrors:
            return hostname, pathInHost
        if not self._selectedRelevant(hostname):
            self._selected[hostname] = [self._select(hostname), time.time()]
        self._selected[hostname][1] = time.time()
        mirror = self._selected[hostname][0]
        realHostname = mirror.split("/")[0]
        mirrorPath = mirror[len(realHostname):]
        assert pathInHost.startswith("/")
        assert len(mirrorPath) == 0 or mirrorPath.startswith("/")
        return realHostname, mirrorPath + pathInHost

    def _selectedRelevant(self, hostname):
        if hostname not in self._selected:
            return False
        MIRROR_SELECTION_TIMEOUT = 60
        return time.time() - self._selected[hostname][1] < MIRROR_SELECTION_TIMEOUT

    def _select(self, hostname):
        for mirror in self._mirrors[hostname]:
            try:
                requests.head('http://' + mirror)
            except:
                pass
            else:
                return mirror
        raise Exception(
            "No mirror responded for '%s', out of '%s'" % (hostname, self._mirrors[hostname]))
