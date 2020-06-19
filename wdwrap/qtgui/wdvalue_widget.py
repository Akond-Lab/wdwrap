#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from PySide2.QtWidgets import QFrame, QVBoxLayout, QLabel, QLineEdit
from wdwrap.param import Parameter


class WdValueWidget(QFrame):

    @staticmethod
    def from_parameter(item):
        return WdValueWidget(item)

    def __init__(self, item: Parameter):
        super().__init__()
        self.item = item
        self.create_controls()

    def create_controls(self):
        l = QVBoxLayout()
        self.label = QLabel(self.item.name())
        l.addWidget(self.label)
        self.edit = QLineEdit(str(self.item))
        l.addWidget(self.edit)
        self.setLayout(l)

