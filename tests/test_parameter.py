"""
Unit tests of WD parameters
"""
import unittest


class TestWD(unittest.TestCase):
    """ Unit tests of WD parameters"""

    def setUp(self):
        pass

    def test_import(self):
        """ Checks default binary construction"""
        import wdwrap.param
        stdev = wdwrap.drivers.STDEV(0.3)
        self.assertGreater(len('{}'.format(stdev)), 0.0)

    def test_copy(self):
        import wdwrap
        b1 = wdwrap.default_binary()
        b2 = b1.copy()
        self.assertGreater(len(b2.lines), 4)
        # after default copy control parameters should remain untached.


if __name__ == '__main__':
    unittest.main()
