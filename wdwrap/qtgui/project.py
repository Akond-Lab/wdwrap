#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import typing

import PySide2
from PySide2.QtCore import QObject, Slot
from wdwrap.bundle import Bundle
from wdwrap.io import Writer_lcin
from wdwrap.curves import LightCurve, VelocCurve
from wdwrap.qtgui.model_bundle import BundleModel
from wdwrap.qtgui.model_curves import CurvesModel, CurveContainer


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

    @Slot()
    def add_lc(self):
        self.curves_model.add_curve(LightCurve(bundle=self.bundle))

    @Slot()
    def add_rv(self):
        self.curves_model.add_curve(VelocCurve(bundle=self.bundle))

    @Slot(CurveContainer)
    def delete_curve(self, to_delete: CurveContainer):
        self.curves_model.delete_curve_container(to_delete)

