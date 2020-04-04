#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import unittest


class TestFileStructure(unittest.TestCase):
    """ Tests config"""

    def setUp(self):
        pass

    def test_filestructure(self):
        from wdwrap.drivers.filestructure import FileStructure
        from wdwrap.drivers import TFINAL
        l = FileStructure.line_classes_list('lcin', '2015', 12)
        self.assertIsInstance(l[7](), TFINAL)


    def test_default(self):
        from wdwrap.config import cfg
        cfg = cfg()
        self.assertIsNotNone(cfg)

    def test_access(self):
        from wdwrap.config.cfg_handler import CfgHandler
        cfg = CfgHandler()
        self.assertGreater(len(cfg.get('executables','lc')), 0)


if __name__ == '__main__':
    unittest.main()
