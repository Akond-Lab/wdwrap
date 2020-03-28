# coding=utf-8
"""Reading and Writing WD files

This module implements classes to read and write files used by WD code"""

#from __future__ import print_function
from os import path
from collections import OrderedDict
from . import parameter as p
from .bundle import Bundle, ParameterSet


class IO(object):
    """Abstract base class for file readers/writers

    File can be given as opened file descriptor (e.g. `sys.stdin`) or pathname string.

    Parameters
    ----------
    filepath : str or file-like
        File to be read, either file-like object or pathname string.
    """

    def __init__(self, filepath):
        super(IO, self).__init__()
        self.filename = None
        self.fd = None
        self.closeonexit = False
        if isinstance(filepath, str):
            self.open_file(filepath=filepath)
        elif filepath is not None:  # suppose open stream
            self.fd = filepath

    def __del__(self):
        if self.closeonexit:
            self.fd.close()

    def open_file(self, filepath):
        """Open file (if not specified in constructor)"""
        self.filename = filepath
        self.fd = self._open(filepath)
        self.closeonexit = True

    def open_default_file(self, filename):
        """Open on of default files provided with module (e.g. WD example files)"""
        self.open_file(self.default_wd_file_abspath(filename))

    def _open(self, filepath):
        raise NotImplementedError('_open method should be overridden')

    @staticmethod
    def default_wd_files_path():
        return path.join(path.dirname(path.abspath(__file__)), 'default_wd_files')

    @staticmethod
    def default_wd_file_abspath(filename):
        return path.join(IO.default_wd_files_path(), filename)


class Reader(IO):
    def _open(self, filepath):
        return open(self.filename, 'r')


class Writer(IO):
    def _open(self, filepath):
        return open(self.filename, 'w')


class Writer_lcin(Writer):
    """lcin files writer

    File can be given as opened file descriptor (e.g. `sys.stdin`) or pathname string.
    The file structure is compatible with LC program lcin files

    Parameters
    ----------
    filepath : str or file-like
        File to be written, either file-like object or pathname string.
    bundle : wdwrap.Bundle or list of wdwrap.Bundle
        List of *bundles* to be written - sets of binary system parameters.
    """

    def __init__(self, filepath=None, bundle=None):
        super(Writer_lcin, self).__init__(filepath)
        self.bundles = self.bundleslist(bundle)   # TODO: Change to ParameterSet

    @staticmethod
    def bundleslist(bundle):
        """If parameter `bundle` is a single Bundle returns `list(bundle)`
        otherwise assumes that parameter is a list already and returns it"""
        if isinstance(bundle, ParameterSet):
            return [bundle]
        else:
            return bundle  # list already

    def write(self):
        for b in self.bundles:
            #  First 8 lines
            for l in b.lines[:8]:
                self._write_line(l)
            ln = 8
            #  Spectral lines
            if b['MPAGE'] == 3:
                for collection in ['spectral1', 'spectral2']:
                    self._write_line(b.lines[ln])
                    ln += 1
                    for _ in b[collection]:
                        self._write_line(b.lines[ln])
                        ln += 1
                    print(p.WLL.nan_value, file=self.fd)  # stop -1.
            # Spots
            for collection in ['spots1', 'spots2']:
                for _ in b.get(collection, []):
                    self._write_line(b.lines[ln])
                    ln += 1
                print(p.XLAT.nan_value, file=self.fd)  # stop 300.
            # Clouds
            for _ in b.get('clouds', []):
                self._write_line(b.lines[ln])
                ln += 1
            print(p.XCL.nan_value, file=self.fd)  # stop 150.
        print(p.MPAGE.nan_value, file=self.fd)  # stop 9.

    def _write_line(self, line):
        # fmt = ''.join([v.fmt_lcin for v in line.values()])
        # print(fmt.format(*line.values()), file=self.fd)
        formatted_lcin = [v.lcin for v in line.values()]
        lns = ' '.join(formatted_lcin)
        print(lns, file=self.fd)


class Reader_lcin(Reader):
    """lcin files reader

    File can be given as opened file descriptor (e.g. `sys.stdin`) or pathname string.
    The file structure must be compatible with LC program lcin files
    File is read automatically on first access to `Reader_lcin.bundles` property (lazy loading)

    Parameters
    ----------
    input : str or file-like
        File to be read, either file-like object or pathname string.
    """

    def __init__(self, filepath=None):
        super(Reader_lcin, self).__init__(filepath)
        self._bundles = None

    @property
    def bundles(self):
        """list of `Bundle`: List of *bundles* read from file - sets of binary system parameters."""
        if self._bundles is None:
            self._read()
        return self._bundles

    def _read(self):
        from . import bundle
        self._bundles = []
        while True:
            ln = self._read_line([p.MPAGE, p.NREF, p.MREF, p.IFSMV1, p.IFSMV2, p.ICOR1, p.ICOR2, p.IF3B, p.LD1, p.LD2])
            if ln['MPAGE'].isnan():
                break
            b = bundle.Bundle()
            self._bundles.append(b)
            b.add_line(ln)
            ln = self._read_line([p.JDPHS, p.HJD0, p.PERIOD, p.DPDT, p.PSHIFT, p.STDEV, p.NOISE, p.SEED])
            b.add_line(ln)
            ln = self._read_line([p.HJDST, p.HJDSP, p.HJDIN, p.PHSTRT, p.PHSTOP, p.PHIN, p.PHN])
            b.add_line(ln)
            ln = self._read_line([p.MODE, p.IPB, p.IFAT1, p.IFAT2, p.N1, p.N2, p.PERR0, p.DPERDT, p.THE, p.VUNIT])
            b.add_line(ln)
            ln = self._read_line([p.E, p.A, p.F1, p.F2, p.VGA, p.XINCL, p.GR1, p.GR2, p.ABUNIN])
            b.add_line(ln)
            ln = self._read_line(
                [p.TAVH, p.TAVC, p.ALB1, p.ALB2, p.POTH, p.POTC, p.RM, p.XBOL1, p.XBOL2, p.YBOL1, p.YBOL2])
            b.add_line(ln)
            ln = self._read_line([p.A3B, p.P3B, p.XINC3B, p.E3B, p.PERR3B, p.TCONJ3B])
            b.add_line(ln)
            ln = self._read_line(
                [p.IBAND, p.HLUM, p.CLUM, p.XH, p.XC, p.YH, p.YC, p.EL3, p.OPSF, p.ZERO, p.FACTOR, p.WL])
            b.add_line(ln)
            if b['MPAGE'] == 3:  # Spectral lines to be generated
                ln = self._read_line([p.BINWM1, p.SC1, p.SL1, p.NF1])
                b.add_line(ln)
                while True:
                    ln = self._read_line([p.WLL, p.EWID, p.DEPTH, p.KKS])
                    if ln['WLL'].isnan():
                        break
                    b.add_line(ln, 'spectral1')
                ln = self._read_line([p.BINWM2, p.SC2, p.SL2, p.NF2])
                b.add_line(ln)
                while True:
                    ln = self._read_line([p.WLL, p.EWID, p.DEPTH, p.KKS])
                    if ln['WLL'].isnan():
                        break
                    b.add_line(ln, 'spectral2')
            # Spots
            for collection in ['spots1', 'spots2']:
                while True:
                    ln = self._read_line([p.XLAT, p.XLONG, p.RADSP, p.TEMSP])
                    if ln['XLAT'].isnan():
                        break
                    b.add_line(ln, collection)
            # Clouds
            while True:
                ln = self._read_line([p.XCL, p.YCL, p.ZCL, p.RCL, p.OP1, p.FCL, p.EDENS, p.XMUE, p.ENCL])
                if ln['XCL'].isnan():
                    break
                b.add_line(ln, 'clouds')

    def _read_line(self, parameters):
        lns = self.fd.readline().split()
        lnd = OrderedDict()
        for cls, val in zip(parameters, lns):
            lnd[cls.name()] = cls(val)
        return lnd


class FixedTableReader(Reader):

    def __init__(self, filepath, columns=None):
        super(FixedTableReader, self).__init__(filepath)
        self._table = None
        self.columns = columns

    @property
    def table(self):
        if self._table is None:
            self._read()
        return self._table

    def _read(self):
        self._table = []
        for l in self.fd:
            if '#' in l[:2]:
                pass
            else:
                row = []
                for s in l.split():
                    if s[-4:-3] == 'D':  # Fortran exponent -> python
                        s = s.replace('D', 'e', 1)
                    row.append(float(s))
                self._table.append(row)


class Reader_light(FixedTableReader):

    def __init__(self, filepath):
        super(Reader_light, self).__init__(filepath,
                                           columns=[15, 15, 12, 12, 12, 12, 12, 10, 11, 11, 16]
                                           )

class Reader_veloc(FixedTableReader):
    pass
