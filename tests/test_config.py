"""
Unit tests of module config
"""
import unittest


class TestConfig(unittest.TestCase):
    """ Tests config"""

    def setUp(self):
        pass

    def test_import(self):
        import wdwrap
        import wdwrap.config

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
