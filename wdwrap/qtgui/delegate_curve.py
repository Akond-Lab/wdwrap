#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import os

import PySide2
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtWidgets import QStyledItemDelegate, QComboBox

from wdwrap.curves import ObservedValues
from wdwrap.qtgui.dataopendialog import DataOpenDialog
from wdwrap.qtgui.delegate_parameters import ParametersTableDelegate


class CurvesTableDelegate(ParametersTableDelegate):
    def createEditor(self, parent: PySide2.QtWidgets.QWidget, option: PySide2.QtWidgets.QStyleOptionViewItem,
                     index: QModelIndex) -> PySide2.QtWidgets.QWidget:
        model = index.model()
        item, column = model.item_and_column(index)
        content = item.content
        if isinstance(content, ObservedValues) and item.parents_column == 'filename':
            # TODO make it better
            if item.parent().parent().get_content().is_rv():
                editor = DataOpenDialog(
                    expected_columns=['hjd', 'rv1', 'rv1_e', 'rv2', 'rv2_e'],
                    all_columns=['hjd', 'ph', 'rv1', 'rv1_e', 'rv2', 'rv2_e', 'instrument'],
                    obligatory_columns=[('hjd', 'ph'), 'rv1', 'rv2']
                )
            else:
                editor = DataOpenDialog(
                    expected_columns=['hjd', 'mag'],
                    all_columns=['hjd', 'ph', 'mag', 'mag_e'],
                    obligatory_columns=[('hjd', 'ph'), 'mag']
                )
            # editor = QFileDialog(directory=os.curdir, caption='Select Data File')
            # editor.setFileMode(QFileDialog.ExistingFile)
        else:
            editor = super().createEditor(parent, option, index)
        return editor

    def setEditorData(self, editor: PySide2.QtWidgets.QWidget, index: PySide2.QtCore.QModelIndex):
        super().setEditorData(editor, index)

    def setModelData(self, editor: PySide2.QtWidgets.QWidget, model: PySide2.QtCore.QAbstractItemModel,
                     index: PySide2.QtCore.QModelIndex):
        if isinstance(editor, QComboBox):
            item, column = model.item_and_column(index)
            vals, labels = item.values_choice(column)
            pos = editor.currentIndex()
            val = list(vals)[pos]
            model.setData(index, val, Qt.EditRole)
        elif isinstance(editor, DataOpenDialog):
            if editor.result() == DataOpenDialog.Accepted:
                file = editor.file
                if file:
                    f = os.path.relpath(file)
                    model.setData(index, (f, editor.df), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    # @pyqtSlot()
    # def currentItemChanged(self):
    #     self.commitData.emit(self.sender())

