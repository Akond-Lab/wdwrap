#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

"""
Unit tests of WD parameters
"""
import unittest

class TestUiCurves(unittest.TestCase):
    def setUp(self):
        pass

    def test_curve_construction(self):
        from wdwrap.curves import LightCurve, VelocCurve
        lc = LightCurve()
        vc = VelocCurve()
        # wdparams has been removed
        # self.assertIsNotNone(lc.wdparams.param_dict['EL3'])
        # self.assertRaises(LookupError, lambda: lc.wdparams.param_dict['XLAT'])

    def test_curve_generation(self):
        from wdwrap.curves import LightCurve
        from wdwrap.bundle import Bundle
        bundle = Bundle.default_binary()
        lc = LightCurve(bundle=bundle)
        lc.gen_values.generate(wait=True)
        values = lc.gen_values.get_values_at()
        print(values)
        self.assertGreater(len(values), 10)

    def test_curve_generation_at_points(self):
        from wdwrap.curves import LightCurve
        from wdwrap.bundle import Bundle
        bundle = Bundle.default_binary()
        lc = LightCurve(bundle=bundle)
        lc.gen_values.generate(wait=True)
        at = [0.0, 0.2, 0.4, 0.9]
        values = lc.gen_values.get_values_at(at)
        print(values)
        self.assertEqual(len(values), len(at))



class TestUiCurveLists(unittest.TestCase):

    def setUp(self):
        pass

    def test_lc_headers_json(self):
        from wdwrap.jupyterui.curveslist import LcCurvesList
        lcs = LcCurvesList()
        lcs.add(band='V', file='qqwqwq.txt')
        self.assertEqual(len(lcs.headers_json()), len(lcs.columns()))

    def test_lc_items_json(self):
        from wdwrap.jupyterui.curveslist import LcCurvesList
        lcs = LcCurvesList()
        lcs.add(band='V', file='qqwqwq.txt')
        self.assertEqual(len(lcs.items_json()), 1)

    def test_rv_items_json(self):
        from wdwrap.jupyterui.curveslist import RvCurvesList
        lcs = RvCurvesList()
        lcs.add(file='qqwqwq.txt')
        self.assertEqual(len(lcs.items_json()), 1)



if __name__ == '__main__':
    unittest.main()
