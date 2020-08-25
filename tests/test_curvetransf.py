#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import unittest
import wdwrap.sample
import wdwrap.curves

class CurveTransformCase(unittest.TestCase):

    def test_phasing(self):
        P = 20.1782302
        T0 = 5096.50028
        lc = wdwrap.sample.sample_lc_dataframe()
        phaser = wdwrap.curves.CurvePhaser(hjd0=T0, period=P)
        lcp = phaser.transform(lc)

        self.assertEqual(len(lcp), len(lc))
        self.assertGreaterEqual(lcp['ph'].min(), 0)
        self.assertLessEqual(lcp['ph'].max(), 1)

    def test_resample(self):
        P = 20.1782302
        T0 = 5096.50028
        lc = wdwrap.sample.sample_lc_dataframe()
        phaser = wdwrap.curves.CurvePhaser(hjd0=T0, period=P)
        resampler = wdwrap.curves.CurveResampler(k=20, active=True)
        lcp = resampler.transform(phaser.transform(lc))
        self.assertEqual(len(lcp), 20)
        self.assertGreaterEqual(lcp['ph'].min(), 0)
        self.assertLessEqual(lcp['ph'].max(), 1)

    def test_resample_noparams(self):
        lc = wdwrap.sample.sample_lc_dataframe()
        phaser = wdwrap.curves.CurvePhaser()
        resampler = wdwrap.curves.CurveResampler()
        lcp = resampler.transform(phaser.transform(lc))
        self.assertEqual(len(lcp), len(lc))
        self.assertGreaterEqual(lcp['ph'].min(), 0)
        self.assertLessEqual(lcp['ph'].max(), 1)

class ConvertedValuesCase(unittest.TestCase):

    def test_transform(self):
        P = 20.1782302
        T0 = 5096.50028
        k = 20
        lc = wdwrap.sample.sample_lc_dataframe()
        t1 = wdwrap.curves.ConvertedValues(df=lc)
        t2 = wdwrap.curves.ConvertedValues()
        t3 = wdwrap.curves.ConvertedValues()
        self.assertEqual(len(t1.df), len(lc))
        self.assertEqual(len(t2.df), 0)
        t1.transformers['phaser'].hjd0 = T0
        t1.transformers['phaser'].period = P
        t1.transformers['resampler'].k = 20
        t1.transformers['resampler'].active = True
        t2.transformers['phaser'].hjd0 = T0
        t2.transformers['phaser'].period = P
        t2.transformers['resampler'].k = k
        t2.transformers['resampler'].active = True
        t2.set_df(lc)
        t3.set_df(lc)
        self.assertEqual(len(t1.df), k)
        self.assertEqual(len(t2.df), k)
        self.assertEqual(len(t3.df), len(lc))
        t3.transformers['phaser'].hjd0 = T0
        t3.transformers['phaser'].period = P
        t3.transformers['resampler'].k = k
        t3.transformers['resampler'].active = True
        self.assertEqual(len(t3.df), k)



if __name__ == '__main__':
    unittest.main()


