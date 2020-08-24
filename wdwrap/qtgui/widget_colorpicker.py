#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

from PySide2.QtCore import Slot, Signal
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QPushButton, QColorDialog

from wdwrap.qtgui.model_connector import HasModelConnector

class SelectColorButton (QPushButton, HasModelConnector):

    changed = Signal(str)

    def __init__(self, color='#000000'):
        self._color: QColor = QColor(color)
        QPushButton.__init__(self)
        HasModelConnector.__init__(self)
        self.clicked.connect(self.open_color_picker)

    def get_slot_and_signal_for_view(self):
        return self.set_color, self.changed

    @property
    def rgb(self):
        return self._color.name()

    @Slot(str)
    def set_color(self, color):
        self._color = QColor(color)
        self._update_button_color()

    @Slot()
    def open_color_picker(self):
        new_color: QColor = QColorDialog.getColor(self._color, self.parentWidget())
        if new_color != self._color:
            self.set_color(new_color)
            self.changed.emit(self.rgb)

    def _update_button_color(self):
        self.setStyleSheet('background-color: ' + self._color.name())

