from collections import OrderedDict


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

    # def __init__(self, params : Optional[Sequence[Mapping[_KT, _VT]]] = None):
    #
    #     pass
    #


