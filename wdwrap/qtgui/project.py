#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import typing

import PySide2
from PySide2.QtCore import QObject
from wdwrap.bundle import Bundle
from wdwrap.io import Writer_lcin
from wdwrap.jupyterui.curves import LightCurve, VelocCurve
from wdwrap.qtgui.model_bundle import BundleModel
from wdwrap.qtgui.model_curves import CurvesModel


class Project(QObject):

    def __init__(self, parent: typing.Optional[PySide2.QtCore.QObject] = None):
        super().__init__(parent)

        self.bundle = Bundle.default_binary()
        self.parameters_model = BundleModel(self.bundle)
        self.curves_model = CurvesModel([
            LightCurve(bundle=self.bundle),
            VelocCurve(bundle=self.bundle),  # TODO: Initial curves
        ])

    def load_bundle(self, filename):
        new_bundle = Bundle.open(filename)
        self.bundle.populate_from(new_bundle)

    def save_bundle(self, filename):
        writer = Writer_lcin(filename, self.bundle)
        writer.write()
