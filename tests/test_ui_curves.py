#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

"""
Unit tests of WD parameters
"""
import unittest


class TestUiCurves(unittest.TestCase):

    def setUp(self):
        pass

    def test_lc_headers_json(self):
        from wdwrap.ui import LcCurvesList
        lcs = LcCurvesList()
        lcs.add(band='V', file='qqwqwq.txt')
        self.assertEqual(len(lcs.headers_json()), len(lcs.columns()))

    def test_lc_items_json(self):
        from wdwrap.ui import LcCurvesList
        lcs = LcCurvesList()
        lcs.add(band='V', file='qqwqwq.txt')
        self.assertEqual(len(lcs.items_json()), 1)

    def test_rv_items_json(self):
        from wdwrap.ui import RvCurvesList
        lcs = RvCurvesList()
        lcs.add(file='qqwqwq.txt')
        self.assertEqual(len(lcs.items_json()), 1)



if __name__ == '__main__':
    unittest.main()
