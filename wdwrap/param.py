import re
import astropy.units as u
from traitlets import HasTraits, Instance

from .fformat import FortranFormatter, Flags, Formatter, FortranDFormatter, FortranZFormatter

u_Rsol = u.Unit("6.95660e5 km")

class F:
    """Namespace to encapsulate FORTRAN formatters"""

    i1 = Formatter('{:1d}', 1)
    x1i1 = Formatter(' {:1d}', 2)
    i2 = Formatter('{:02d}', 2)
    x1i2 = Formatter(' {:02d}', 3)
    is2 = Formatter('{:+2d}', 2)
    x1is2 = Formatter(' {:+2d}',3)
    i3 = Formatter(' {:02d}', 3)
    i4 = Formatter(' {:03d}', 4)
    i5 = Formatter(' {:04d}', 5)

    f17_8 = FortranZFormatter(' {:016.8f}', 17)
    f15_6 = FortranZFormatter(' {:014.6f}', 15)
    f14_6 = FortranZFormatter(' {:013.6f}', 14)
    f13_6 = FortranZFormatter(' {:012.6f}', 13)
    f12_6 = FortranZFormatter(' {:011.6f}', 12)
    f11_5 = FortranZFormatter(' {:010.5f}', 11)
    f11_0 = FortranZFormatter(' {:09.0f}.', 11)
    f10_7 = FortranZFormatter(' {:09.7f}', 10)
    f10_6 = FortranZFormatter(' {:09.6f}', 10)
    f10_5 = FortranZFormatter(' {:09.5f}', 10)
    f10_4 = FortranZFormatter(' {:09.4f}', 10)
    f9_6  = FortranZFormatter(' {:08.6f}', 9)
    f9_5  = FortranZFormatter(' {:08.5f}', 9)
    f9_4  = FortranZFormatter(' {:08.4f}', 9)
    f9_3  = FortranZFormatter(' {:08.3f}', 9)
    f9_2  = FortranZFormatter(' {:08.2f}', 9)
    f8_4  = FortranZFormatter(' {:07.4f}', 8)
    f8_3  = FortranZFormatter(' {:07.4f}', 8)
    f8_2  = FortranZFormatter(' {:07.2f}', 8)
    f7_5  = FortranZFormatter(' {:06.5f}', 7)
    f7_4  = FortranZFormatter(' {:06.4f}', 7)
    f7_3  = FortranZFormatter(' {:06.3f}', 7)
    f7_2  = FortranZFormatter(' {:06.2f}', 7)
    f6_5  = FortranZFormatter('{:6.5f}', 6)

    d17_10 = FortranDFormatter(' {:16.10e}', 17)
    d14_7 =  FortranDFormatter(' {:13.7e}', 14)
    d13_6 =  FortranDFormatter(' {:12.6e}', 13)
    d13_5 =  FortranDFormatter(' {:12.5e}', 13)
    d12_6 =  FortranDFormatter(' {:11.6e}', 12)
    d12_5 =  FortranDFormatter(' {:11.5e}', 12)
    d11_5 =  FortranDFormatter(' {:10.5e}', 11)
    d11_4 =  FortranDFormatter(' {:10.4e}', 11)
    d11_3 =  FortranDFormatter(' {:10.3e}', 11)
    d10_4 =  FortranDFormatter(' {:9.4e}', 10)

class ParFlag:
    none        = 0b00000000
    controlling = 0b00000001  #  does not affect model
    fittable    = 0b00000010  #  can be fitted (by DC)
    curvedep    = 0b00000100  #  curve specific (may be different for different curves)
    outputspec  = 0b00001000  #  affects only output e.g. points
    lc          = 0b00010000  #  LC in
    dc          = 0b00100000  #  DC in
    curvepriv   = 0b01000000  #  set for all curve calcualtion independently (may not be presented in UI)

class Parameter(HasTraits):
    format_str = '{}'
    fmt_lcin = '{}'
    help_str = 'parameter'
    help_val = None
    max = None
    min = None
    unit = None
    nan_value = None
    flags = ParFlag.none
    val = Instance(object, allow_none=True)

    def __init__(self, val=None):
        super(Parameter, self).__init__()
        if isinstance(val, str):
            self.from_str(val)
        else:
            self.val = val
        self.fix = True

    def __str__(self):
        return self.format_str.format(self.val)

    def __repr__(self):
        frmt = '{:s}={:s}'
        ret = frmt.format(self.name(), str(self))
        if self.help_val:
            ret += '({:s})'.format(self.help_val[int(self)])
        return ret

    # def __format__(self, format_spec: str) -> str:
    #     return ('{:' + format_spec + '}').format(self)

    @classmethod
    def format(cls, val, fmt):
        return fmt.format(val)

    def isnan(self):
        return self.val == self.nan_value

    def is_controlling(self):
        return bool(self.flags & ParFlag.controlling)

    def from_str(self, val):
        self.val = self.scan_str(val)

    @classmethod
    def scan_str(cls, val):
        raise NotImplementedError('from_str method should be overridden')

    def to_python(self):
        """Coverts variable to corresponding python type"""
        raise NotImplementedError('to_python method should be overridden')

    @property
    def lcin(self):
        return self.format(self.val, self.fmt_lcin)

    @property
    def doc(self):
        return self.__doc__

    @classmethod
    def name(cls):
        return cls.__name__

class FloatParameter(Parameter):
    def __float__(self):
        return float(self.val)

    @classmethod
    def scan_str(cls, val):
        return float(re.sub('[dD]', 'e', val, 1))

    def to_python(self):
        """Coverts variable to corresponding python type"""
        return float(self)


class IntParameter(Parameter):
    def __int__(self):
        return int(self.val)

    @classmethod
    def scan_str(cls, val):
        return int(val)

    def to_python(self):
        """Coverts variable to corresponding python type"""
        return int(self)

    def help_str_value(self):
        """help string corresponding to value """
        if self.help_val is None:
            return str(self.val)
        else:
            return self.help_val[self.val]

