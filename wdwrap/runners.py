from __future__ import print_function
import shutil
import os
import re
from tempfile import mkdtemp
import subprocess as subprocess
from .io import Writer_lcin
from .config import default_cfg

class TmpDir:
    """
    instances of TmpDir keeps track and lifetime of temporary directory
    """
    path = None

    def __init__(self, delete_on_exit=False):
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


class Runner(object):
    def __init__(self):
        super(Runner, self).__init__()

class LcRunner(object):

    def __init__(self):
        super(LcRunner, self).__init__()
        cfg = default_cfg()
        self.executable = cfg.get('executables', 'lc')

    def run(self, bundle):
        with WdTempDir() as d:
            self.write_lcin(bundle, d)
            proc = subprocess.Popen([self.executable], cwd=d, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            outs, errs = proc.communicate()
            errors = re.search(r'error:\s*(.*)', errs)
            if errors:
                raise RuntimeError('lc error: ' + errors.groups()[0])
            # print (errs)
            # print (d)

    def write_lcin(self, bundle, dir, filename='lcin.active'):
        w = Writer_lcin(filepath=os.path.join(dir, filename), bundle=bundle)
        w.write()

