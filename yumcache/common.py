from yumcache import objectstore
from yumcache import bogusurls


class Common:
    def __init__(self, storePath, bogusURLs):
        self.objectStore = objectstore.ObjectStore(storePath)
        self.bogusURLs = bogusurls.BogusURLs(bogusURLs)
