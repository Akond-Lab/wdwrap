#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

from PySide2.QtCore import Qt
from PySide2.QtGui import QColor

from wdwrap.param import Parameter, ParFlag
from wdwrap.qtgui.container import Container


_logger = None
def logger():
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('param container')
    return _logger

class WdParameterContainer(Container):
    @property
    def wdpar(self) -> Parameter:
        p = self.content
        return p

    def data(self, column: str, role: int):
        # if role not in [Qt.DisplayRole, Qt.EditRole, Qt.CheckStateRole]:
        #     return None
        ret = super().data(column, role)
        try:
            if ret is None:
                if role == Qt.BackgroundColorRole:
                    if self.wdpar.flags & ParFlag.curvepriv:
                        ret = QColor('gainsboro')
                    elif self.wdpar.flags & ParFlag.curvedep:
                        ret = QColor('aquamarine')
                elif column == 'value' and role in [Qt.DisplayRole, Qt.EditRole]:
                    try:
                        ret = f'{self.wdpar}: {self.wdpar.help_val[self.wdpar.val]}'
                    except (AttributeError, LookupError, TypeError):
                        ret = str(self.wdpar)
                elif column == 'description' and role in [Qt.DisplayRole]:
                    ret = self.wdpar.help_str
                elif column == 'description' and role in [Qt.ToolTipRole]:
                    ret = self.wdpar.__doc__
                elif column == 'help' and role in [Qt.DisplayRole]:
                    ret = self.wdpar.__doc__
                elif column == 'min' and role in [Qt.DisplayRole, Qt.EditRole]:
                    ret = self.wdpar.val_min
                elif column == 'max' and role in [Qt.DisplayRole, Qt.EditRole]:
                    ret = self.wdpar.val_max
                elif column == 'fit' and role in [Qt.CheckStateRole]:
                    if self.wdpar.flags & ParFlag.fittable:
                        ret = Qt.Unchecked if self.wdpar.fix else Qt.Checked
                # elif column == 'fit' and role in [Qt.DisplayRole, Qt.EditRole]:
                #     ret = not self.wdpar.fix

        except AttributeError:
            pass
        return ret

    def values_choice(self, column='value'):
        if column == 'value':
            return self.wdpar.values_choice()
        else:
            return None, None


    def set_data(self, column: str, role: int, data):
        if role not in [Qt.EditRole, Qt.CheckStateRole]:
            return False

        ret = False
        try:
            if isinstance(data, str):
                data = self.content.scan_str(data)
            if column == 'value':
                self.content.val = data
                ret = True
            elif column == 'min':
                self.content.val_min = data
                ret = True
            elif column == 'max':
                self.content.val_max = data
                ret = True
            elif column == 'fit':
                self.content.fix = not bool(data)
                ret = True
        except ValueError as e:
            logger().exception(f'Wrong value "{data}"', exc_info=e)
        except Exception as e:
            raise e
        return ret

    # def editable(self, column: str):
    #     if column in ['value', 'min', 'max', 'fit']:
    #         return True
    #     else:
    #         return False

    def flags(self, column: str, flags):
        if column in ['value']:
            if False and self.wdpar.flags & ParFlag.controlling:  # not for now
                flags &= ~Qt.ItemIsEnabled
            else:
                flags |= Qt.ItemIsEditable
        elif column in ['min', 'max']:
            if self.wdpar.flags & ParFlag.fittable:
                flags |= Qt.ItemIsEditable
        elif column in ['fit']:
            if self.wdpar.flags & ParFlag.fittable:
                flags |= Qt.ItemIsUserCheckable
        return flags