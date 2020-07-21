from collections import OrderedDict
from typing import Iterator, Tuple

from .drivers.filestructure import FileStructure
from .param import ParFlag, Parameter


class ParameterSet(OrderedDict):

    def __init__(self):
        super(ParameterSet, self).__init__()
        self.lines = []

    def add_line(self, ln, collection=None):
        self.lines.append(ln)
        if collection:
            if collection not in self.keys():
                self[collection] = []
            self[collection].append(ln)
        else:
            self.update(ln)

    def copy(self):
        import copy
        new = self.__class__(self)
        for line in self.lines:
            newline = OrderedDict()
            for k, v in line.items():
                if v.is_controlling():
                    newline[k] = copy.copy(v) # Copy Control parameters
                else:
                    newline[k] = v
            new.add_line(newline)
        new.reindex()
        return new

    def reindex(self):
        super(ParameterSet, self).clear()
        for line in self.lines:
            self.update(line)

    def clear(self):
        self.lines = []
        super(ParameterSet, self).clear()

    def set_value(self, key: int, value):
        """phoebe style, equivalent `to b[key] = val` """
        self[key] = value

    def iter(self, flags_any=None, flags_all=None, flags_not=None, classes=None) -> Iterator[Tuple[str, Parameter]]:
        for key, item in self.items():
            if flags_any is not None and not item.flags & flags_any:
                continue
            if flags_all is not None and not (item.flags & flags_all) == flags_all:
                continue
            if flags_not is not None and not (item.flags & flags_not) == ParFlag.none:
                continue
            if classes is not None and type(item) not in classes:
                continue
            yield key, item

    def observe(self, handler, flags_any=None, flags_all=None, flags_not=None, classes=None):
        for key, item in self.iter(flags_any=flags_all, flags_all=flags_all, flags_not=flags_not, classes=classes):
            item.observe(handler)



    # def __init__(self, params : Optional[Sequence[Mapping[_KT, _VT]]] = None):
    #
    #     pass
    #


