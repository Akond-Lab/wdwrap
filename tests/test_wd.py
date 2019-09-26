"""
Unit tests of WD invocation
"""
import unittest
import sys


class TestWD(unittest.TestCase):
    """ Tests Running WD Code"""

    def setUp(self):
        pass

    def test_default_files(self):
        """ Checks if there is an access to default file"""
        import os
        from wdwrap.bundle import Bundle

        self.assertTrue(
            os.path.isfile(Bundle.default_wd_file_abspath('lcin_original.active'))
        )

    def test_default_binary(self):
        """ Checks default binary construction"""
        import wdwrap
        self.assertIsNotNone(
            wdwrap.default_binary()
        )

    def test_bundle_repr(self):
        import wdwrap
        b = wdwrap.default_binary()
        r = repr(b)
        self.assertIsNotNone(r)

    def test_lc_multi_bundle_read_write(self):
        from wdwrap.io import Writer_lcin, Reader_lcin
        r = Reader_lcin()
        r.open_default_file('lcin.2007.dat1')
        bs = r.bundles
        self.assertEqual(len(bs), 2)  # Two bundles in file
        w = Writer_lcin(sys.stdout, bs)
        w.write()

    def test_lc_read_write_read(self):
        try:
            from StringIO import StringIO  # Python 2
        except ImportError:
            from io import StringIO        # Python 3
        import wdwrap
        from wdwrap.io import Writer_lcin, Reader_lcin
        buf = StringIO()
        b1 = wdwrap.default_binary()
        w = Writer_lcin(buf, [b1])
        w.write()
        bufs = buf.getvalue()
        buf.seek(0)
        r = Reader_lcin(buf)
        b2 = r.bundles[0]
        self.assertEqual(b1, b2)





if __name__ == '__main__':
    unittest.main()
