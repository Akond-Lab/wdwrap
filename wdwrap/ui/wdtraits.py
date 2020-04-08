#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

from traitlets import HasTraits, Float, Int, Enum, Bool, List
from ..param import Parameter, FloatParameter, IntParameter, ParFlag
from ..drivers.filestructure import FileStructure
from ..bundle import ParameterSet
from ..config import cfg

class WdParamTrait(HasTraits):

    fit = Bool(allow_none=True)

    def __init__(self, *args, pclass=None, value=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pclass = None
        # self.fit = None
        if pclass is None and isinstance(value, Parameter):
            pclass = type(value)
        if pclass is not None:
            self.setup_wdclass(pclass)
            if value is not None:
                if isinstance(value, Parameter):
                    self.set_from_parameter(value)
                else:
                    self.value = value
        elif value is not None:
            raise TypeError(f'pclass not specified in constructor, can not initialize with value {value}')

    def setup_wdclass(self, pclass):
        # pclass = VGA
        self.pclass = pclass
        kwargs = {}
        if pclass.min is not None:
            kwargs['min'] = pclass.min
        if pclass.max is not None:
            kwargs['max'] = pclass.max
        kwargs['help'] = pclass.doc
        kwargs['allow_none'] = True
        kwargs['default_value'] = None
        if issubclass(pclass, FloatParameter):
            self.add_traits(val=Float(**kwargs))
        elif issubclass(pclass, IntParameter):
            if pclass.help_val:  # enum
                self.add_traits(val=Enum(values=pclass.help_val, **kwargs))
            else:  # int
                self.add_traits(val=Int(**kwargs))
        else:
            raise TypeError(f'No WdPramTrait for class {pclass} (IntParameter and FloatParameter supported) ')
        if pclass.flags & ParFlag.fittable:
            self.fit = False

    def set_from_parameter(self, value: Parameter):
        self.value = value.val


class WdParamTraitCollection(HasTraits):
    params = List()

    def __init__(self, *args, flags_any=None, flags_all=None, flags_not=None, wdversion=None, **kwargs):
        super().__init__(*args, **kwargs)

        if flags_any or flags_all or flags_not:
            self.initialize_according_to_flags(flags_any=flags_any, flags_all=flags_all, flags_not=flags_not,
                                               wdversion=wdversion)

    def initialize_according_to_flags(self, flags_any=None, flags_all=None, flags_not=None, lines=None, wdversion=None):
        if wdversion is None:
            wdversion = cfg().get('executables', 'version')
        lst = FileStructure.line_classes_list('lcin', wdversion, line_no=lines)
        if flags_any:
            lst = [c for c in lst if c.flags & flags_any]
        if flags_all:
            lst = [c for c in lst if (c.flags & flags_all) == flags_all]
        if flags_not:
            lst = [c for c in lst if (c.flags & flags_not) == ParFlag.none]
        self.initialize_with_classes(lst)

    def initialize_with_classes(self, pclasslst):
        for c in pclasslst:
            self.params.append(WdParamTrait(pclass=c))

    def read_bundle(self, bundle: ParameterSet, set_fit=False):
        for p in self.params:
            try:
                wdp = bundle[p.pclass.name()]
            except LookupError:
                continue
            p.value = wdp.val
            if p.fit is not None and set_fit:
                p.fit = not wdp.fix

    def write_bundle(self, bundle: ParameterSet, set_fit=True):
        for p in self.params:
            try:
                wdp = bundle[p.pclass.name()]
            except LookupError:
                continue
            wdp.val = p.value
            if p.fit is not None and set_fit:
                wdp.fix = not p.fit

