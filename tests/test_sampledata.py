#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import unittest


class SampledataCase(unittest.TestCase):
    def test_lc_filepath(self):
        from wdwrap.sample import sample_lc_filepath
        self.assertGreater(len(sample_lc_filepath()), 0)
        self.assertGreater(len(sample_lc_filepath('B')), 0)
        self.assertGreater(len(sample_lc_filepath(obs='WASP', band=None)), 0)

    def test_rv_filepath(self):
        from wdwrap.sample import sample_rv_filepath
        self.assertGreater(len(sample_rv_filepath()), 0)

    def test_lc_fileexists(self):
        import os
        from wdwrap.sample import sample_lc_filepath
        self.assertTrue(os.path.isfile(sample_lc_filepath()))
        self.assertTrue(os.path.isfile(sample_lc_filepath('B')))
        self.assertTrue(os.path.isfile(sample_lc_filepath(obs='WASP', band=None)))

    def test_rv_fileexists(self):
        import os
        from wdwrap.sample import sample_rv_filepath
        self.assertTrue(os.path.isfile(sample_rv_filepath()))

    def test_light_dat_fileexists(self):
        import os
        from wdwrap.sample import sample_light_dat_filepath
        self.assertTrue(os.path.isfile(sample_light_dat_filepath()))

    def test_lc_dataframe(self):
        from wdwrap.sample import sample_lc_dataframe
        self.assertGreater(len(sample_lc_dataframe()), 0)
        self.assertGreater(len(sample_lc_dataframe('B')), 0)
        self.assertGreater(len(sample_lc_dataframe(obs='WASP', band=None)), 0)

    def test_light_dat_dataframe(self):
        from wdwrap.sample import sample_light_dat_dataframe
        self.assertGreater(len(sample_light_dat_dataframe()), 0)

    def test_rv_dataframe(self):
            from wdwrap.sample import sample_rv_dataframe
            self.assertGreater(len(sample_rv_dataframe()), 0)

if __name__ == '__main__':
    unittest.main()
