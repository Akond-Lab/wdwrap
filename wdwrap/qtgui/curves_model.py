#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import logging
from typing import Optional, List

from wdwrap.bundle import Bundle
from wdwrap.jupyterui.curves import WdCurve
from wdwrap.qtgui.container import Container, PropertiesAccessContainer, ParentColumnContainer
from wdwrap.qtgui.containerstree_model import ContainesTreeModel, ColumnsPreset
from wdwrap.qtgui.wpparameter_container import WdParameterContainer

logging.getLogger().setLevel(logging.DEBUG)

class CurveContainer(PropertiesAccessContainer):
    pass

class CurveObservedContainer(PropertiesAccessContainer):
    pass

class CurveGeneratedContainer(Container):
    pass

class CurvesModel(ContainesTreeModel):
    def __init__(self, curves: Optional[List[WdCurve]] = None, parent=None):
        self.curves = curves
        super().__init__(parent)
        self.columns = ColumnsPreset(['name', 'data'])

    def build_qmodel(self):
        for n, l in enumerate(self.curves):
            try:
                name = f'curve {n} {l.obs_values.filename}'
            except AttributeError:
                name = f'curve {n}'
            c = CurveContainer(name, l, self.display_root)
            ParentColumnContainer('plot', c)
            ParentColumnContainer('fit', c)
            CurveGeneratedContainer('generated', l.gen_values, c)
            o = CurveObservedContainer('observed', l.obs_values, c)
            ParentColumnContainer('bins', o)
            ParentColumnContainer('min', o)
            ParentColumnContainer('max', o)
