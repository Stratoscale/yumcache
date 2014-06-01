import os


class ObjectStore:
    def __init__(self, root):
        self._root = root
        if not os.path.isdir(root):
            os.makedirs(root)

    def notFound(self, path):
        if not os.path.exists(self._notFoundPath(path)):
            return False
        with open(self._notFoundPath(path), "rb") as f:
            count = int(f.read())
        return count > 10

    def exists(self, path):
        return os.path.exists(self._rootedPath(path))

    def read(self, path):
        with open(self._rootedPath(path), "rb") as f:
            return f.read()

    def write(self, path, content):
        self._mkdirFor(self._rootedPath(path))
        with open(self._rootedPath(path), "wb") as f:
            f.write(content)

    def incrementNotFoundCount(self, path):
        if os.path.exists(self._notFoundPath(path)):
            with open(self._notFoundPath(path), "rb") as f:
                count = int(f.read()) + 1
        else:
            count = 1
        self._mkdirFor(self._notFoundPath(path))
        with open(self._notFoundPath(path), "wb") as f:
            f.write(str(count))

    def _rootedPath(self, path):
        return os.path.join(self._root, path.strip( '/' ) + "_response" )

    def _notFoundPath(self, path):
        return os.path.join(self._root, path.strip( '/' ) + "_notFound" )

    def _mkdirFor(self, path):
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
