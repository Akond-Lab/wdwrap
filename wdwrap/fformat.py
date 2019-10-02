# coding=utf-8
"""Formatters for FORTRAN number syntax"""

import re

class Flags:
    none    = 0
    ZERO    = 0b00000001    # leading zeros
    NOZERO  = 0b00000010    # no 0 before decimal .
    SIGN    = 0b00000100    # always +/- sign
    DECDOT  = 0b00001000    # suffix with decimal dot



class FortranFormatter(object):
    """FORTRAN style formatter

    Attributes
    ----------
    flags : Flags
        Formatting flags
    frmt : str
        Corresponding python format string

    Parameters
    ----------
    type : str
        FORTRAN type, e.g. 'f' in `f10.3` FORTRAN format. One of: [i f e d x]
    len : int
        Field length, e.g. 8 in `i8` FORTRAN format
    dec : int
        Decimal places, e.g. 3 in `f10.3` FORTRAN format
    flags : int
        Additional formatting flags as defined in 'Flags' enumeration
    """

    def __init__(self, fortran_type, len, dec = 0, flags = Flags.none):
        super(FortranFormatter, self).__init__()
        self.type = fortran_type
        self.len = len
        self.dec = dec
        self.flags = flags
        self.fmt = self._pythonfmt()

    def _pythonfmt(self):
        if self.type == 'x':
            return ' '*self.len
        t = self.type
        if t == 'i':
            t = 'd'
        elif t == 'd':
            t = 'e'
        fmt = '{:'
        if self.flags & Flags.SIGN:
            fmt += '+'
        if self.flags & Flags.ZERO:
            fmt += '0'
        fmt += str(self.len)
        if t in 'fe':  # float
            fmt += '.' + str(self.dec)
        fmt += t + '}'
        return fmt

    def format(self, val):
        s = self.fmt.format(val)
        if self.flags & Flags.NOZERO or len(s) > self.len:  # cut leading 0
            s = re.sub(r'0\.', '.', s)
        if self.type == 'd':
            s = re.sub(r'[eE]', 'd', s)
        if self.flags & Flags.DECDOT and self.type == 'f' and s[0] in ' 0' and '.' not in s:
            s = s[1:] + '.'
        return s


class Formatter(object):
    """OBSOLETE """

    def __init__(self, fmt=None, fixlen=None):
        super(Formatter, self).__init__()
        if fmt:
            self.fmt = fmt
        else:
            self.fmt = '{}'
        self.fixlen = fixlen

    def format(self, val):
        return self.fmt.format(val)

class FortranZFormatter(Formatter):
    """OBSOLETE used FORTRAN formatting without leading zero e.g. f4.3: .123 instead of 0.123"""
    def format(self, val):
        s = super(FortranZFormatter, self).format(val)
        if self.fixlen and len(s) > self.fixlen:
            s = re.sub('0\.', '.', s)
        return s

class FortranDFormatter(FortranZFormatter):
    """OBSOLETE used FORTRAN formatting had letter 'd' as exponential delimiter"""
    def format(self, val):
        return super(FortranDFormatter, self).format(val).replace('e', 'd')