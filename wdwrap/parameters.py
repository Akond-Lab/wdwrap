from collections import OrderedDict
from typing import Iterator, Tuple, Mapping, overload, Iterable

from traitlets import traitlets

from .drivers.filestructure import FileStructure
from .param import ParFlag, Parameter


# TODO: Refactor and clarify lines.

class ParameterSet(OrderedDict):
    # Filters for elements selection
    filter_every = lambda v: True
    filter_none = lambda v: False
    filter_curve = lambda v: bool(v.flags & (ParFlag.curvedep | ParFlag.curvepriv))

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
            self._update_parameters_set(ln)

    def __setitem__(self, k, v):
        if isinstance(v, (Parameter, list)):
            super().__setitem__(k, v)
            for l in self.lines:
                if k in l.keys():
                    l[k] = v
        else:
            el = self[k]
            el.val = v

    def copy(self):
        raise NotImplementedError('Use clone() instead')

    def update_filtered(self, source, filter_condition=filter_every):
        source = source.clone()
        filtered = {k: v for k, v in source.items() if filter_condition(v)}
        self.update_parameters(filtered)

    def _update_parameters_set(self, source):
        super().update(source)

    def update_parameters(self, source: dict):
        try:
            lines = source.lines  # new is ParameterSet preserve new lines composition
        except AttributeError:
            lines = self.lines  # new is not ParameterSet, update lines of self, as they are
        for k, v in source.items():
            for l in lines:
                if k in l.keys():  # update line value
                    lid = self._line_id(l)
                    l_to_update = self._line_from_id(lid)
                    if l_to_update is not None:
                        l_to_update[k] = v
        self._update_parameters_set(source)


    def update(self, *args, **kwargs) -> None:
        raise NotImplementedError('do not call  `ParameterSet.update()`, use ParameterSet.update_parameters()')

    def clone(self, deap_copy_condition=filter_every):
        import copy
        new = self.__class__(self)
        for line in self.lines:
            newline = OrderedDict()
            for k, v in line.items():
                if deap_copy_condition(v):
                    newline[k] = copy.deepcopy(v)  # Copy Control parameters
                else:
                    newline[k] = v
            new.add_line(newline)
        new.reindex()
        return new

    def populate_from(self, source: 'ParameterSet'):
        import copy
        # lines identified by first element's name
        source_lines = [self._line_id(l) for l in source.lines]

        # remove lines not existing in source
        for n, line in enumerate(self.lines):
            if self._line_id(line) not in source_lines:
                names = [par.name() for par in line.values()]
                for name in names:
                    del self[name]
                self.lines[n] = None
        self.lines = [l for l in self.lines if l is not None]

        self_lines = [self._line_id(l) for l in self.lines]
        for n, line in enumerate(source.lines):
            id = source._line_id(line)
            if id == self._line_number_id(n):  # we have source line, copy values
                for k, v in line.items():
                    self[k].val = v.val
            else:
                newline = OrderedDict()
                for k, v in line.items():
                    toadd = copy.copy(v)
                    newline[k] = toadd
                    self[k] = toadd
                self.lines.insert(n, newline)

    @staticmethod
    def _line_id(line):
        return next(iter(line))

    def _line_number_id(self, n):
        try:
            return self._line_id(self.lines[n])
        except LookupError:
            return None

    def _line_from_id(self, lid):
        for l in self.lines:
            if self._line_id(l) == lid:
                return l
        return None

    def reindex(self):
        super(ParameterSet, self).clear()
        for line in self.lines:
            self._update_parameters_set(line)

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

    def observe(self, handler, flags_any=None, flags_all=None, flags_not=None, classes=None, names=traitlets.All):
        """Traitlets observe (sub)set of bundle parameters"""
        for key, item in self.iter(flags_any=flags_any, flags_all=flags_all, flags_not=flags_not, classes=classes):
            item.observe(handler, names=names)

    def unobserve(self, handler, flags_any=None, flags_all=None, flags_not=None, classes=None):
        """Traitlets observe (sub)set of bundle parameters"""
        for key, item in self.iter(flags_any=flags_any, flags_all=flags_all, flags_not=flags_not, classes=classes):
            item.unobserve(handler)

    # def __init__(self, params : Optional[Sequence[Mapping[_KT, _VT]]] = None):
    #
    #     pass
    #
