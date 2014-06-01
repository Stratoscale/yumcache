
class GrowingBlob:
    """
    python is slow in accumulation of large data (str += segment).
    Growing blob is an optimization for that
    """
    def __init__(self):
        self._blobs = []
        self._length = 0

    def append(self, blob):
        self._blobs.append(blob)
        self._length += len(blob)

    def length(self):
        return self._length

    def content(self):
        return "".join(self._blobs)

    def substr(self, start, ceil):
        if ceil > self._length:
            ceil = self._length
        offset = start
        length = ceil - offset
        result = ""
        for blob in self._blobs:
            if length == 0:
                break
            if offset > len(blob):
                offset -= len(blob)
                continue
            else:
                subblob = blob[offset: offset + length]
                result += subblob
                offset = 0
                length -= len(subblob)
        return result
