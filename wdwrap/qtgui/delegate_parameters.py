#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import PySide2
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtWidgets import QStyledItemDelegate, QComboBox


class ParametersTableDelegate(QStyledItemDelegate):
    def createEditor(self, parent: PySide2.QtWidgets.QWidget, option: PySide2.QtWidgets.QStyleOptionViewItem,
                     index: QModelIndex) -> PySide2.QtWidgets.QWidget:
        item, column = index.model().item_and_column(index)
        vals, labels = item.values_choice(column)
        if vals:
            editor = QComboBox(parent)
            editor.insertItems(0, labels)
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
        else:
            super().setModelData(editor, model, index)

    # @pyqtSlot()
    # def currentItemChanged(self):
    #     self.commitData.emit(self.sender())

