#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import typing
from datetime import datetime

import yaml

import PySide2
from PySide2.QtCore import QObject, Slot
from wdwrap.bundle import Bundle
from wdwrap.io import Writer_lcin
from wdwrap.curves import LightCurve, VelocCurve
from wdwrap.qtgui.model_bundle import BundleModel
from wdwrap.qtgui.model_curves import CurvesModel, CurveContainer
from wdwrap.version import version_tuple


_logger = None
def logger():
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('project')
    return _logger


class Project(QObject):

    def __init__(self, parent: typing.Optional[PySide2.QtCore.QObject] = None):
        super().__init__(parent)

        self.bundle = Bundle.default_binary()
        self.parameters_model = BundleModel(self.bundle)
        self.curves_model = CurvesModel([
            VelocCurve(bundle=self.bundle),  # TODO: Initial curves
            LightCurve(bundle=self.bundle),
        ])

    def load_bundle(self, filename):
        new_bundle = Bundle.open(filename)
        self.bundle.populate_from(new_bundle)

    def save_bundle(self, filename):
        writer = Writer_lcin(filename, self.bundle)
        writer.write()

    def save_project(self, filename, mode='default'):
        header = {
                'format': 'YAML',
                'info': 'This is project file of the Wilson-Devinney Code wrapper (WDW) '
                        'https://github.com/Akond-Lab/wdwrap',
                'save mode': mode,
                'filename': filename,
                'wdw version': list(version_tuple),
                'timestamp local': datetime.now().isoformat(),
                'timestamp utc': datetime.utcnow().isoformat(),
            }
        prj = {'wdw project': {
            'header': header,
            'data': self.to_dict(),
        }}
        with open(filename, 'w') as f:
            yaml.dump(prj, f, sort_keys=False, default_flow_style=None, width=500)

    def open_project(self, filename) -> bool:
        with open(filename, 'r') as f:
            try:
                prj = yaml.load(f)
            except IOError:
                logger().error(f'Loading project from YAML file {filename} failed')
                return False
        try:
            try:
                data = prj['wdw project']['data']
            except LookupError:
                logger().error('Loading: no "data"')
                return False
            self.from_dict(data)
        except ValueError:
            return False
        return True

    def to_dict(self):
        ret = {
            'wd_parameters': self.bundle.to_dict(),
            'curves': {o.objectName(): o.content.to_dict() for o in self.curves_model.curves_iter()},
            # 'curves': [c.to_dict() for c in self.curves_model.curves],
        }
        return ret

    def from_dict(self, data):
        # should not be needed
        self.curves_model.delete_all_curve_containers()
        try:
            self.bundle.from_dict(data['wd_parameters'])
        except LookupError:
            logger().info('Loading: no "wd_parameters" section')
            return
        try:
            curves = {}
            for name, cdict in data['curves'].items():
                if cdict['rv']:
                    c = VelocCurve(bundle=self.bundle)
                else:
                    c = LightCurve(bundle=self.bundle)
                c.from_dict(cdict)
                curves[name] = c
        except LookupError:
            logger().info('Loading: no "curves" section?')
            return
        self.curves_model.add_curves(curves=curves, replace=True)


    @Slot()
    def add_lc(self):
        self.curves_model.add_curve(LightCurve(bundle=self.bundle))

    @Slot()
    def add_rv(self):
        self.curves_model.add_curve(VelocCurve(bundle=self.bundle))

    @Slot(CurveContainer)
    def delete_curve(self, to_delete: CurveContainer):
        self.curves_model.delete_curve_container(to_delete)

