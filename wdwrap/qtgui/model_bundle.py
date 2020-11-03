#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

from wdwrap.bundle import Bundle
from wdwrap.qtgui.container import Container
from wdwrap.qtgui.model_containerstree import ContainersTreeModel, ColumnsPreset
from wdwrap.qtgui.model_wpparameter import WdParameterContainer

class BundleModel(ContainersTreeModel):
    def __init__(self, bundle: Bundle = None, parent=None):
        self.bundle = bundle
        super().__init__(parent)
        self.columns = ColumnsPreset(['name', 'value', 'fit', 'min', 'max', 'description'])

    def build_qmodel(self):
        self.display_root = Container('bundle', self.bundle, self.root)
        for n, l in enumerate(self.bundle.lines):
            line = Container(f'Line {n}', l, self.display_root)
            for key, item in l.items():
                WdParameterContainer(key, item, line)
        # d1 = Container('dupa1', None, self.bundle_qmodel)
        # d2 = Container('dupa2', None, d1)
        # d3 = Container('dupa3', None, d2)
