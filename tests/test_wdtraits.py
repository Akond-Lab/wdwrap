#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import unittest


class WdTraitsCase(unittest.TestCase):

    def test_WdParamTraitCollection(self):
        from wdwrap.ui.wdtraits import WdParamTraitCollection
        from wdwrap.param import ParFlag
        c1 = WdParamTraitCollection(flags_any=ParFlag.lc)
        c2 = WdParamTraitCollection(flags_any=ParFlag.lc|ParFlag.curvedep)
        c3 = WdParamTraitCollection(flags_all=ParFlag.lc|ParFlag.curvedep)
        self.assertEqual(len(c1.params), len(c2.params))
        self.assertGreater(len(c2.params), len(c3.params))

    def test_TraitCollectionReadWrite(self):
        from wdwrap.ui.wdtraits import WdParamTraitCollection
        from wdwrap.bundle import Bundle
        from wdwrap.param import ParFlag
        c = WdParamTraitCollection(flags_any=ParFlag.lc)
        b1 = Bundle.default_binary()
        b2 = Bundle.default_binary()
        b1['HJD0'] = 1.111
        self.assertAlmostEqual   (float(b1['HJD0']), 1.111)
        self.assertNotAlmostEqual(float(b2['HJD0']), 1.111)
        c.read_bundle(b1)
        c.write_bundle(b2)
        self.assertAlmostEqual   (float(b2['HJD0']), 1.111)


if __name__ == '__main__':
    unittest.main()
