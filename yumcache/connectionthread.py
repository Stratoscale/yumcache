import socket
import logging
import traceback
import threading
from yumcache import request
from yumcache import cachedresponse
from yumcache import liveresponse
from yumcache import downloader


class ConnectionThread(threading.Thread):
    def __init__(self, connection, common):
        self._connection = connection
        self._common = common
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def run(self):
        try:
            while True:
                self._handleRequest()
        except request.NoMoreRequests:
            pass
        except:
            traceback.print_exc()
        finally:
            try:
                self._connection.shutdown(socket.SHUT_WR)
            except:
                pass
            self._connection.close()

    def _handleRequest(self):
        req = request.Request(self._connection)
        if self._common.objectStore.notFound(req.path()):
            cachedresponse.CachedResponse(self._connection).respondNotFound()
        elif self._common.objectStore.exists(req.path()):
            logging.info("Using cache %(path)s", dict(path=req.path()))
            cachedresponse.CachedResponse(self._connection).respond(
                self._common.objectStore.read(req.path()), req.range())
        else:
            realHostname, realPath = self._common.bogusURLs.replace(
                req.hostname(), req.pathInHost())
            url = "http://%s%s" % (realHostname, realPath)
            downloaderInstance = downloader.Downloader(self._common, req.path(), url)
            liveresponse.LiveResponse(self._connection, downloaderInstance, req.range()).replay()
