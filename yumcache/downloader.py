import requests
import logging
import urllib2
import traceback
import threading
from yumcache import growingblob


class Downloader(threading.Thread):
    INVALID_LENGTH = -1

    def __init__(self, common, path, url):
        self._common = common
        self._path = path
        self._url = url
        self._content = None
        self._error = None
        self._length = None
        self._done = False
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def content(self):
        return self._content

    def error(self):
        return self._error

    def length(self):
        return self._length

    def done(self):
        return self._done

    def run(self):
        try:
            self._work()
        except:
            logging.exception("Downloader thread exited with exception")
        finally:
            self._done = True

    def _work(self):
        downloadedCompletly = False
        try:
            self._findLength()
        except:
            original = traceback.format_exc()
            try:
                self._completeDownload()
                downloadedCompletly = True
            except:
                logging.exception(
                    "Unable to find length of %(url)s, and even complete download failed. "
                    "Original Stack trace:\n%(originalException)s", dict(
                        url=self._url, originalException=original))
                self._common.objectStore.incrementNotFoundCount(self._path)
                raise
        if not downloadedCompletly:
            self._liveDownload()
        self._write()

    def _completeDownload(self):
        response = requests.get(self._url)
        self._content = growingblob.GrowingBlob()
        self._content.append(response.content)
        self._length = self._content.length()
        self._statusCode = response.status_code

    def _findLength(self):
        RETRIES = 10
        for retry in xrange(RETRIES):
            try:
                self._length = self._findLengthRetry(retry)
                break
            except:
                if retry == RETRIES - 1:
                    logging.exception("Unable to determine length of %(url)s", dict(url=self._url))
                    raise

    def _liveDownload(self):
        RETRIES = 5
        for retry in xrange(RETRIES):
            try:
                logging.info("Downloading '%(url)s'", dict(url=self._url))
                self._retryLiveDownload(retry)
                logging.info("Done Downloading '%(url)s'", dict(url=self._url))
                break
            except:
                logging.exception("While Downloading '%(url)s'", dict(url=self._url))
                if retry == RETRIES - 1:
                    logging.exception("Unable to download %(url)s", dict(url=self._url))
                    self._error = traceback.format_exc()
                    raise

    def _retryLiveDownload(self, retry):
        req = urllib2.Request(self._url, headers={'accept-encoding': ''})
        session = urllib2.urlopen(req, timeout=15)
        try:
            self._content = growingblob.GrowingBlob()
            while True:
                data = session.read(1024 * 16)
                if data == "":
                    if self._length != self.INVALID_LENGTH and self._content.length() != self._length:
                        raise Exception(
                            "Transfer interrupted of %(url)s: expected %(length)d bytes, "
                            "transferred only %(transferred)d bytes. retrying", dict(
                                url=self._url, length=self._length,
                                transferred=self._content.length()))
                    return
                self._content.append(data)
        finally:
            self._statusCode = session.getcode()
            session.close()

    def _write(self):
        try:
            if self._statusCode != 200:
                logging.info(
                    "Not writing cache for '%(url)s', statusCode was %(statusCode)d "
                    "(and not 200)", dict(url=self._url, statusCode=self._statusCode))
                return
            if self._length != self.INVALID_LENGTH and self._content.length() != self._length:
                raise Exception("Internal error %d != %d" % (self._content.length(), self._length))
            self._common.objectStore.write(self._path, self._content.content())
            logging.info("Done writing cache for '%(url)s'", dict(url=self._url))
        except:
            logging.exception("Unable to write cache for %(url)s", dict(url=self._url))
            self._error = traceback.format_exc()
            raise

    def _findLengthRetry(self, retry):
        length = self._findLengthUsingASingleHead(retry)
        MAKE_SURE_ATTEMPTS = 2
        for i in xrange(MAKE_SURE_ATTEMPTS):
            another = self._findLengthUsingASingleHead(retry)
            if length != another:
                raise Exception(
                    "Got two different length responses (%(first)d, %(second)d) for the "
                    "same url %(url)s", dict(
                        first=length, second=another, url=self._url))
        return length

    def _findLengthUsingASingleHead(self, retry):
        response = requests.head(
            self._url, allow_redirects=True, timeout=15, headers={'accept-encoding': ''})
        if response.status_code != 200:
            raise Exception(
                "Unable to find length, status code was: %(statusCode)d",
                dict(statusCode=response.status_code))
        return int(response.headers.get('content-length', self.INVALID_LENGTH))
