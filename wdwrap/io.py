# coding=utf-8
"""Reading and Writing WD files

This module implements classes to read and write files used by WD code"""

#from __future__ import print_function
from os import path
import io
import logging
from collections import OrderedDict
import pandas as pd
from . import drivers as p
from .bundle import ParameterSet
from .drivers.filestructure import FileStructure


class IO(object):
    """Abstract base class for file readers/writers

    File can be given as opened file descriptor (e.g. `sys.stdin`) or pathname string.

    Parameters
    ----------
    filepath : str or file-like
        File to be read, either file-like object or pathname string.
    """

    def __init__(self, filepath=None):
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

    def open_text(self, text: str=None, filename=None):
        self.filename = filename
        if text is not None:
            self.fd = io.StringIO(text)

    def open_bytes(self, text: bytes=None, filename=None):
        self.filename = filename
        if text is not None:
            self.fd = io.BytesIO(text)

    def open_default_file(self, filename, subdir=''):
        """Open on of default files provided with module (e.g. WD example files)"""
        self.open_file(self.default_wd_file_abspath(filename, subdir=subdir))

    def _open(self, filepath):
        raise NotImplementedError('_open method should be overridden')

    @staticmethod
    def default_wd_files_path(subdir=''):
        return path.join(path.dirname(path.abspath(__file__)), 'default_wd_files', subdir)

    @staticmethod
    def default_wd_file_abspath(filename, subdir=''):
        return path.join(IO.default_wd_files_path(subdir=subdir), filename)


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
    filepath : str or file-like
        File to be read, either file-like object or pathname string.
    version : WD version
    """

    def __init__(self, filepath=None, version=None):
        super(Reader_lcin, self).__init__(filepath)
        self._bundles = None
        if version is None:
            from .config import cfg
            version = cfg().get('executables', 'version')
        self.version = version

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
            ln = self._read_line_no(0)
            if ln['MPAGE'].isnan():
                break
            b = bundle.Bundle()
            self._bundles.append(b)
            b.add_line(ln)
            ln = self._read_line_no(1)
            b.add_line(ln)
            ln = self._read_line_no(2)
            b.add_line(ln)
            ln = self._read_line_no(3)
            b.add_line(ln)
            ln = self._read_line_no(4)
            b.add_line(ln)
            ln = self._read_line_no(5)
            b.add_line(ln)
            ln = self._read_line_no(6)
            b.add_line(ln)
            ln = self._read_line_no(7)
            b.add_line(ln)
            if b['MPAGE'] == 3:  # Spectral lines to be generated
                ln = self._read_line_no(8) #[p.BINWM1, p.SC1, p.SL1, p.NF1])
                b.add_line(ln)
                while True:
                    ln = self._read_line_no(9) #[p.WLL, p.EWID, p.DEPTH, p.KKS])
                    if ln['WLL'].isnan():
                        break
                    b.add_line(ln, 'spectral1')
                ln = self._read_line_no(10) # [p.BINWM2, p.SC2, p.SL2, p.NF2])
                b.add_line(ln)
                while True:
                    ln = self._read_line_no(11) # [p.WLL, p.EWID, p.DEPTH, p.KKS])
                    if ln['WLL'].isnan():
                        break
                    b.add_line(ln, 'spectral2')
            # Spots
            for collection in ['spots1', 'spots2']:
                while True:
                    ln = self._read_line_no(12) #[p.XLAT, p.XLONG, p.RADSP, p.TEMSP])
                    if ln['XLAT'].isnan():
                        break
                    b.add_line(ln, collection)
            # Clouds
            while True:
                ln = self._read_line_no(13) #[p.XCL, p.YCL, p.ZCL, p.RCL, p.OP1, p.FCL, p.EDENS, p.XMUE, p.ENCL])
                if ln['XCL'].isnan():
                    break
                b.add_line(ln, 'clouds')

    def _read_line_no(self, line_no: int):
        return self._read_line(FileStructure.line_classes_list('lcin', self.version, line_no))
        
    def _read_line(self, parameters):
        lns = self.fd.readline().split()
        lnd = OrderedDict()
        for cls, val in zip(parameters, lns):
            try:
                lnd[cls.name()] = cls(val)
            except (ValueError, TypeError) as e:
                logging.exception(f'Cannot create instance of {cls.name()} initialized with {val}', exc_info=e)
                raise e
        return lnd

class DataFrameReader(Reader):
    def __init__(self, filepath=None, columns=None):
        super(DataFrameReader, self).__init__(filepath)
        self._df = None
        self.columns = columns

    @property
    def df(self):
        """Returns data as pandas DataFrame"""
        if self._df is None:
            self._df = self._read()
        return self._df

    def _read(self):
        return pd.read_table(self.fd, delim_whitespace=True, comment='#', header=None,
                             names=self.columns['names'] if self.columns else None)

class FixedTableReader(DataFrameReader):

    def __init__(self, filepath=None, columns=None):
        super(FixedTableReader, self).__init__(filepath, columns=columns)

    def _read(self):
        table = []
        for l in self.fd:
            if '#' in l[:2]:
                pass
            else:
                row = []
                for s in l.split():
                    if s[-4:-3] == 'D':  # Fortran exponent -> python
                        s = s.replace('D', 'e', 1)
                    row.append(float(s))
                table.append(row)
        return pd.DataFrame(table, columns=self.columns['names'])


class Reader_light(FixedTableReader):
    """Reads light curve generated by LC"""

    def __init__(self, filepath=None):
        super(Reader_light, self).__init__(filepath,
                                           columns={
                                               'names':  ['hjd', 'ph', 'L1', 'L2', 'Lcombined', 'Lnorm',
                                                          'separation', 'magnorm', 'mag', 'timeshift'],
                                               'widths': [15, 15, 12, 12, 12, 12, 12, 10, 11, 11, 16]
                                           })

class Reader_veloc(FixedTableReader):
    """Reads rv curve generated by LC"""

    def __init__(self, filepath=None):
        super(Reader_veloc, self).__init__(filepath,
                                           columns={
                                               'names':  ['hjd', 'ph', 'relrv1', 'relrv2', 'eclipsecorr1',
                                                          'eclipsecorr2', 'rv1', 'rv2', 'timeshift'],
                                           })


class Reader_ravespan_rv(DataFrameReader):
    """Reads Ravespan RV curve"""
    def __init__(self, filepath=None):
        super(Reader_ravespan_rv, self).__init__(filepath,
                                           columns={
                                               'names':  ['hjd', 'rv1', 'rv1_e', 'rv2', 'rv2_e', 'instr'],
                                           })

    def _read(self):
        return pd.read_table(self.fd, delim_whitespace=True, comment='#',
                             names=self.columns['names'])

class Reader_hjd_mag(DataFrameReader):
    """Reads two columns [hjd, mag]"""
    def __init__(self, filepath=None, hjdcol=0, magcol=1):
        super(Reader_hjd_mag, self).__init__(filepath,
                                           columns={
                                               'names':  ['hjd', 'mag'],
                                           })
        self.hjdcol = hjdcol
        self.magcol = magcol


    def _read(self):
        return pd.read_table(self.fd, delim_whitespace=True, comment='#',
                             names=self.columns['names'],
                             usecols=[self.hjdcol, self.magcol])

