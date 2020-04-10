#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

"""
Unit tests of WD parameters
"""
import unittest

class TestUiCurves(unittest.TestCase):
    def setUp(self):
        pass

    def test_curve_contruction(self):
        from wdwrap.ui.curves import LightCurve, VelocCurve
        lc = LightCurve()
        vc = VelocCurve()
        self.assertIsNotNone(lc.wdparams.param_dict['EL3'])
        self.assertRaises(LookupError, lambda: lc.wdparams.param_dict['XLAT'])

class TestUiCurveLists(unittest.TestCase):

    def setUp(self):
        pass

    def test_lc_headers_json(self):
        from wdwrap.ui.curveslist import LcCurvesList
        lcs = LcCurvesList()
        lcs.add(band='V', file='qqwqwq.txt')
        self.assertEqual(len(lcs.headers_json()), len(lcs.columns()))

    def test_lc_items_json(self):
        from wdwrap.ui.curveslist import LcCurvesList
        lcs = LcCurvesList()
        lcs.add(band='V', file='qqwqwq.txt')
        self.assertEqual(len(lcs.items_json()), 1)

    def test_rv_items_json(self):
        from wdwrap.ui.curveslist import RvCurvesList
        lcs = RvCurvesList()
        lcs.add(file='qqwqwq.txt')
        self.assertEqual(len(lcs.items_json()), 1)



if __name__ == '__main__':
    unittest.main()
