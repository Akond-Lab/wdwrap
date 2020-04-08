#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import unittest
import wdwrap.sample
import wdwrap.ui.curves

class CurveTransformCase(unittest.TestCase):

    def test_phasing(self):
        P = 20.1782302
        T0 = 5096.50028
        lc = wdwrap.sample.sample_lc_dataframe()
        phaser = wdwrap.ui.curves.CurvePhaser(hjd0=T0, period=P)
        lcp = phaser.transform(lc)

        self.assertEqual(len(lcp), len(lc))
        self.assertGreaterEqual(lcp['ph'].min(), 0)
        self.assertLessEqual(lcp['ph'].max(), 1)

    def test_resample(self):
        P = 20.1782302
        T0 = 5096.50028
        lc = wdwrap.sample.sample_lc_dataframe()
        phaser = wdwrap.ui.curves.CurvePhaser(hjd0=T0, period=P)
        resampler = wdwrap.ui.curves.CurveResampler(k=20)
        lcp = resampler.transform(phaser.transform(lc))
        self.assertEqual(len(lcp), 20)
        self.assertGreaterEqual(lcp['ph'].min(), 0)
        self.assertLessEqual(lcp['ph'].max(), 1)

    def test_resample_noparams(self):
        lc = wdwrap.sample.sample_lc_dataframe()
        phaser = wdwrap.ui.curves.CurvePhaser()
        resampler = wdwrap.ui.curves.CurveResampler()
        lcp = resampler.transform(phaser.transform(lc))
        self.assertEqual(len(lcp), len(lc))
        self.assertGreaterEqual(lcp['ph'].min(), 0)
        self.assertLessEqual(lcp['ph'].max(), 1)


if __name__ == '__main__':
    unittest.main()


