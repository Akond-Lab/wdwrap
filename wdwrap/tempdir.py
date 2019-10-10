import os
import shutil
from tempfile import mkdtemp

from .io import Writer_lcin


class TmpDir:
    """
    instances of TmpDir keeps track and lifetime of temporary directory
    """
    path = None

    def __init__(self, delete_on_exit=True):
        self.delete_on_exit = delete_on_exit
        self.path = mkdtemp(prefix='wdwrap_')
        self._init_dir()

    def _init_dir(self):
        pass

    def __del__(self):
        if self.delete_on_exit:
            self.rm_dir()

    def __enter__(self):
        return self.path

    def __exit__(self, type_, value, traceback):
        if self.delete_on_exit:
            self.rm_dir()

    def __str__(self):
        return self.path

    def rm_dir(self):
        try:
            shutil.rmtree(self.path)
        except OSError:
            pass


class WdTempDir(TmpDir):

    def _init_dir(self):
        TmpDir._init_dir(self)
        for f in ['atmcof.dat', 'atmcofplanck.dat']:
            os.symlink(Writer_lcin.default_wd_file_abspath(f), os.path.join(self.path, f))