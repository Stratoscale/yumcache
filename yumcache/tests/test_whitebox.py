from yumcache.tests import fakeserver
from yumcache.tests import yumcachewrapper
import unittest
import urllib2
import os


class Test(unittest.TestCase):
    def setUp(self):
        self.server = fakeserver.FakeServer()
        self.wrapper = yumcachewrapper.YumCacheWrapper()

    def tearDown(self):
        self.wrapper.done()
        if self.server is not None:
            self.server.done()

    def write(self, relativeFilename, contents):
        path = os.path.join(self.server.directory(), relativeFilename)
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "wb") as f:
            f.write(contents)

    def test_FakeServer(self):
        self.write("yuvu", "the contents")
        connection = urllib2.urlopen("http://localhost:%d/yuvu" % fakeserver.PORT)
        try:
            contents = connection.read()
        finally:
            connection.close()
        self.assertEquals(contents, "the contents")

    def download(self, path):
        connection = urllib2.urlopen("http://localhost:%d/localhost:%d/%s" % (
            yumcachewrapper.PORT, fakeserver.PORT, path))
        try:
            return connection.read()
        finally:
            connection.close()

    def test_FetchOneFile(self):
        self.write("yuvu", "the contents")
        self.assertEquals(self.download("yuvu"), "the contents")

    def test_FetchOneSeveralTimes(self):
        self.write("yuvu", "the contents")
        self.assertEquals(self.download("yuvu"), "the contents")
        self.assertEquals(self.download("yuvu"), "the contents")
        self.assertEquals(self.download("yuvu"), "the contents")

    def test_FetchWhileServerIsDead(self):
        self.write("yuvu", "the contents")
        self.assertEquals(self.download("yuvu"), "the contents")
        self.server.done()
        self.server = None
        self.assertEquals(self.download("yuvu"), "the contents")


if __name__ == '__main__':
    unittest.main()
