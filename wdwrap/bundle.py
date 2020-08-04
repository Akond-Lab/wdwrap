# coding=utf-8
import pandas as pd
from .config import cfg
from .parameters import ParameterSet
from .param import Parameter
from .drivers import MPAGE
#from .parameter import MPAGE


from .config import cfg



class Bundle(ParameterSet):
    class FileFormatError(Exception):
        pass
    class FileFormatMultipleSetsError(FileFormatError):
        pass
    class FileFormatNotSupportedError(FileFormatError):
        pass

    def __init__(self, wdversion=None):
        super(Bundle, self).__init__()
        if wdversion is None:
            wdversion = cfg().get('executables', 'version')
        self.wdversion = wdversion
        self._light = None
        self._veloc = None

    def copy(self):
        ret = super().copy()
        ret.wdversion = self.wdversion
        ret._light = self._light
        ret._veloc = self._veloc
        return ret

    def populate_from(self, source):
        super().populate_from(source)
        self.wdversion = source.wdversion


    @classmethod
    def default_binary(cls, default_file=None, bundleno=0):
        from .io import Reader_lcin
        if default_file is None:
            wdversion = cfg().get('executables', 'version')
            default_file = f'lcin.default.{wdversion}.active'
        b = cls.open(Reader_lcin.default_wd_file_abspath(default_file), bundleno=bundleno)
        return b

    @classmethod
    def open(cls, filepath, bundleno=0):
        from .io import Reader_lcin
        reader = Reader_lcin(filepath)
        bundle = reader.bundles[bundleno]
        if len(bundle.lines) > 8:
            raise cls.FileFormatNotSupportedError('Clouds and Spots not supported (yet)')
        return bundle

    def __repr__(self):
        return '\n'.join([
            ' '.join([repr(v) for v in l.values()])
            for l in self.lines
        ])

    def __setitem__(self, k, v):
        if isinstance(v, (Parameter, list)):
            super(Bundle, self).__setitem__(k, v)
        else:
            el = self[k]
            el.val = v

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def lc(self):
        """Runs WD `lc` program. No need to be called directly

        An access to `light` or `veloc` properties calculates data if needed"""
        from .runners import LcRunner
        r = LcRunner()
        return r.run(self)

    def run_compute(self):
        """Alias of `lc()`"""
        self.lc()


    def reset(self):
        """Resets cashed results from lc"""
        self._light = None
        self._veloc = None

    @property
    def light(self):
        """Calculated (by LC) light curve pandas DataFrame"""
        if self._light is None:
            self['MPAGE'] = MPAGE.LIGHT
            ret = self.lc()
            self._light = ret['light']
        return self._light

    @light.setter
    def light(self, val):
        self._light = val

    @property
    def veloc(self):
        """Calculated (by LC) radial velocity curve, returns pandas DataFrame"""
        if self._veloc is None:
            self['MPAGE'] = MPAGE.VELOC
            ret = self.lc()
            self._veloc = ret['veloc']
        return self._veloc

    @veloc.setter
    def veloc(self, val):
        self._veloc = val





