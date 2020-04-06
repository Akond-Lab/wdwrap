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
        from wdwrap.io import Reader_lcin

        self.assertTrue(
            os.path.isfile(Reader_lcin.default_wd_file_abspath('lcin.default.2007.active'))
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
        b['PERIOD'] = 2
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

    @unittest.skip('Not implelented')
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
        print (b)
        b.lc(generate='light', filter='B')
        plot(b.light)
        bufs = buf.getvalue()
        buf.seek(0)
        r = Reader_lcin(buf)
        b2 = r.bundles[0]
        self.assertEqual(b1, b2)

    def test_lc_runner(self):
        import wdwrap
        from wdwrap.runners import LcRunner
        r = LcRunner()
        r.run(wdwrap.default_binary())

    def test_bundle_lc_run_light(self):
        import wdwrap
        b = wdwrap.default_binary()
        self.assertGreater(len(b.light), 10)

    def test_bundle_lc_run_rv(self):
        import wdwrap
        b = wdwrap.default_binary()
        b['MPAGE'] = wdwrap.drivers.MPAGE.VELOC
        b.lc()
        self.assertGreater(len(b.veloc), 10)

    def test_bundle_lc_run_rv_auto(self):
        import wdwrap
        b = wdwrap.default_binary()
        self.assertGreater(len(b.veloc), 10)


    def test_phoebe_style(self):
        import wdwrap
        b = wdwrap.default_binary()
        # b.set_value('teff', component='secondary', value=5000)
        # b.set_value('q', value=0.75)
        # b.add_dataset('lc', times=phoebe.linspace(0, 2, 101))
        # b.add_dataset('rv', times=phoebe.linspace(0, 2, 101))
        # b.run_compute()
        # b.plot(show=True)
        b.set_value('TAVH', value=5)
        b.set_value('RM', value=0.75)
        b.run_compute()


        self.assertGreater(len(b.veloc), 10)


if __name__ == '__main__':
    unittest.main()
