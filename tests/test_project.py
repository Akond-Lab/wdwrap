#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import unittest


class ProjectTestCase(unittest.TestCase):

    def test_project_construction(self):
        from wdwrap.ui import Project
        p = Project()

    def test_project_default_values(self):
        from wdwrap.ui import Project
        p = Project()
        self.assertIsNotNone(p.light_curves[0].wdparams['IBAND'])
        self.assertIsNotNone(p.veloc_curves[0].wdparams['IBAND'])
        self.assertIsNotNone(p.control_parameters['MPAGE'])
        self.assertIsNotNone(p.model_parameters['YCL'])

    def test_project_bundle_rw(self):
        from wdwrap.ui import Project
        p = Project()
        import wdwrap
        b1 = wdwrap.default_binary()
        b2 = wdwrap.default_binary()
        b1.set_value('TAVH', value=5)
        b1.set_value('RM', value=0.75)

        self.assertAlmostEqual(b1['TAVH'].val, 5)
        self.assertAlmostEqual(b1['RM'].val, 0.75)
        self.assertNotAlmostEqual(b2['TAVH'].val, 5)
        self.assertNotAlmostEqual(b2['RM'].val, 0.75)
        p.read_bundle(b1)
        p.write_bundle(b2)
        self.assertAlmostEqual(b2['TAVH'].val, 5)
        self.assertAlmostEqual(b2['RM'].val, 0.75)


if __name__ == '__main__':
    unittest.main()
