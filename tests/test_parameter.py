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
        import wdwrap.parameter
        stdev = wdwrap.parameter.STDEV(0.3)
        self.assertGreater(len('{:s}'.format(stdev)), 0.0)


if __name__ == '__main__':
    unittest.main()
