from yumcache.growingblob import GrowingBlob
import unittest

class Test(unittest.TestCase):
    def test_Normal(self):
        tested = GrowingBlob()
        tested.append("abc")
        tested.append("def")
        tested.append("ghi")

        self.assertEquals(tested.length(), 9)
        self.assertEquals(tested.content(), "abcdefghi")
        for i in xrange(9):
            for j in xrange(i, 9 + 1):
                self.assertEquals(tested.substr(i, j), "abcdefghi"[ i : j ])

if __name__ == '__main__':
    unittest.main()
