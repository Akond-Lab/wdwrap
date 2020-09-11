#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from typing import Optional

from PySide2.QtWidgets import QLabel

from wdwrap.param import IntParameter
from wdwrap.qtgui.model_curves import CurveContainer


class CurveKindLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.curve_container: Optional[CurveContainer] = None
        self._model_handler = lambda change: self.update_from_model()

    def connect_model(self, item_model):
        try:
            self.iband_parameter.unobserve(self._model_handler)
        except (AttributeError, ValueError):
            pass
        self.curve_container = item_model
        self.update_from_model()
        if not self.curve_container.is_rv():
            self.iband_parameter.observe(self._model_handler, 'val')

    @property
    def iband_parameter(self) -> Optional[IntParameter]:
        try:
            return self.curve_container.content.gen_values.parameters['IBAND']
        except (AttributeError, LookupError):
            return None

    def update_from_model(self):
        try:
            if self.curve_container.is_rv():
                self.setText('RV')
            else:
                iband = self.iband_parameter
                if iband is not None:
                    self.setText(str(self.iband_parameter.help_str_value()))
                else:
                    self.setText('?')
        except AttributeError:
            self.setText('?')
