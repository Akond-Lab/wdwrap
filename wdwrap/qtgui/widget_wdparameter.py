#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from threading import Lock
from typing import Optional

from PySide2.QtCore import QSize, Slot
from PySide2.QtWidgets import QWidget, QLineEdit, QLayout, QBoxLayout, QVBoxLayout, QComboBox

from wdwrap.param import Parameter, IntParameter


class WdParameterEditBase(QWidget):

    def __init__(self, prop, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setSizeConstraint(self.layout.SetFixedSize)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self._updating_semaphore = Lock()
        self.property = prop
        self.widgets = []
        self.wdparameter: Optional[Parameter] = None
        self._model_handler = lambda change: self._on_model_changed(change)

    def add_subwidget(self, widget: QWidget):
        self.layout.addWidget(widget)
        self.setSizePolicy(widget.sizePolicy())

    # def minimumSizeHint(self) -> QSize:
    #     size = super().minimumSizeHint()
    #     for w in self.children():
    #         size.expandedTo(w.minimumSizeHint())
    #     return size
    #
    # def sizeHint(self) -> QSize:
    #     size = super().sizeHint()
    #     for w in self.children():
    #         size.expandedTo(w.sizeHint())
    #     return size

    def set_parameter(self, parameter: Parameter):
        try:
            self.wdparameter.unobserve(self._model_handler, self.property)
        except (AttributeError, ValueError):
            pass
        self.wdparameter = parameter
        self.update_from_model()
        self.wdparameter.observe(self._model_handler, self.property)

    def update_from_model(self):
        try:
            self._updating_semaphore.acquire(blocking=False)
            if self.wdparameter is None:
                self.set_view_value('')
            else:
                val = getattr(self.wdparameter, self.property)
                self.set_view_value(val)
        finally:
            self._updating_semaphore.release()

    def _on_model_changed(self, change):
        if not self._updating_semaphore.locked():
            self.update_from_model()

    def set_view_value(self, value):
        raise NotImplementedError

    def set_model_value(self, value):
        try:
            if self._updating_semaphore.acquire(blocking=True):
                setattr(self.wdparameter, self.property, value)
        finally:
            self._updating_semaphore.release()


class _WdParameterMinMaxEdit(WdParameterEditBase):

    def __init__(self, prop, parent=None):
        super().__init__(prop, parent)
        self.edit_widget = QLineEdit()
        self.add_subwidget(self.edit_widget)
        self.edit_widget.editingFinished.connect(self.on_text_edited)

    @Slot()
    def on_text_edited(self):
        if self.wdparameter is not None:
            try:
                val = self.wdparameter.scan_str(self.edit_widget.text())
            except:
                self.update_from_model()
                return
            self.set_model_value(val)


    def set_view_value(self, value):
        if value is None:
            value = ''
        elif not isinstance(value, str):
            if isinstance(self.wdparameter, IntParameter):
                value = f'{value:.0f}'
            else:
                value = f'{value:g}'
        self.edit_widget.setText(value)


class WdParameterMinEdit(_WdParameterMinMaxEdit):
    def __init__(self,parent=None):
        super().__init__('val_min', parent)

class WdParameterMaxEdit(_WdParameterMinMaxEdit):
    def __init__(self,parent=None):
        super().__init__('val_max', parent)


class WdParameterValueEdit(WdParameterEditBase):

    def __init__(self, parent=None):
        super().__init__('val', parent)
        self.edit_widget = QLineEdit()
        self.combo_widget = QComboBox()
        self.add_subwidget(self.edit_widget)
        self.add_subwidget(self.combo_widget)
        self.combo_widget.setVisible(False)
        self.edit_widget.editingFinished.connect(self.on_text_edited)
        self.combo_widget.activated.connect(self.on_combo_selected)

    def set_parameter(self, parameter: Parameter):
        use_combo = parameter.help_val is not None
        self.combo_widget.setVisible(use_combo)
        self.edit_widget.setVisible(not use_combo)
        if use_combo:
            vals, labels = parameter.values_choice()
            self.combo_widget.clear()
            self.combo_widget.addItems(labels)
        else:
            self.combo_widget.clear()
        super().set_parameter(parameter)

    @Slot()
    def on_text_edited(self):
        if self.wdparameter is not None:
            try:
                val = self.wdparameter.scan_str(self.edit_widget.text())
            except:
                self.update_from_model()
                return
            self.set_model_value(val)

    @Slot(int)
    def on_combo_selected(self, index: int):
        if self.wdparameter is not None:
            vals, labels = self.wdparameter.values_choice()
            val = list(vals)[index]
            self.set_model_value(val)


    def set_view_value(self, value):
        if value is None:
            value = ''
        if not isinstance(value, str):
            vals, labels = self.wdparameter.values_choice()
            if labels:
                try:
                    index = vals.index(value)
                except ValueError:
                    index = -1
                self.combo_widget.setCurrentIndex(index)
            else:
                if isinstance(self.wdparameter, IntParameter):
                    value = f'{value:.0f}'
                else:
                    value = f'{value:g}'
                self.edit_widget.setText(value)
        else:
            self.edit_widget.setText(value)
            self.combo_widget.setEditText(value)
