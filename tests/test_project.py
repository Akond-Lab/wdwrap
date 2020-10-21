#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import tempfile
import unittest


class ProjectTestCase(unittest.TestCase):

    def test_project_construction(self):
        from wdwrap.jupyterui import Project
        p = Project()

    def test_project_default_values(self):
        from wdwrap.jupyterui import Project
        p = Project()
        # self.assertIsNotNone(p.light_curves[0].wdparams['IBAND'])
        # self.assertIsNotNone(p.veloc_curves[0].wdparams['IBAND'])
        self.assertIsNotNone(p.parameters['MPAGE'])
        self.assertIsNotNone(p.parameters['YCL'])

    def test_project_bundle_rw(self):
        from wdwrap.jupyterui import Project
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


    def test_project_add_curve(self):
        from wdwrap.jupyterui import Project
        p = Project()
        n = len(p.light_curves)
        observed = False
        def h(change):
            nonlocal observed
            observed = True
        p.observe(h, 'light_curves_len')
        self.assertFalse(observed)
        p.new_curve(rv=False)
        self.assertGreater(len(p.light_curves), n)
        self.assertTrue(observed)

        import ipywidgets as widgets
        widgets.FileUpload
        import ipyvuetify as v
        v.DataTable()


if __name__ == '__main__':
    unittest.main()


class ProjectOpenSaveCase(unittest.TestCase):

    @staticmethod
    def generate_project_curves(p: 'Project'):
        for c in p.curves_model.curves:  # ensure generated values are present
            c.gen_values.refresh(wait=True)

    def test_to_from_dict(self):
        from wdwrap.qtgui.project import Project
        p1 = Project()
        p2 = Project()
        p1.bundle['IBAND'] = 10
        self.generate_project_curves(p1)
        self.assertNotEqual(p1.bundle['IBAND'].val, p2.bundle['IBAND'].val)
        d = p1.to_dict()
        p2.from_dict(d)
        self.assertEqual(p1.bundle['IBAND'].val, p2.bundle['IBAND'].val)

    def test_to_from_project_file(self):
        from wdwrap.qtgui.project import Project
        p1 = Project()
        p2 = Project()
        p1.bundle['IBAND'] = 10
        self.generate_project_curves(p1)
        self.assertNotEqual(p1.bundle['IBAND'].val, p2.bundle['IBAND'].val)

        # filename = tempfile.mktemp()
        filename = '/tmp/test_to_from_project_file.wdw'
        d = p1.save_project(filename, mode='unit test')
        ret = p2.open_project(filename)
        self.assertTrue(ret)
        self.assertEqual(p1.bundle['IBAND'].val, p2.bundle['IBAND'].val)