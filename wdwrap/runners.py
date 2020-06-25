from __future__ import print_function
import os
import re
import subprocess32 as subprocess

from .tempdir import WdTempDir
from .io import *
from .config import cfg


class Runner(object):
    def __init__(self):
        super(Runner, self).__init__()

class LcRunner(Runner):

    def __init__(self):
        super(LcRunner, self).__init__()
        self.executable = cfg().get('executables', 'lc')

    def run(self, bundle):
        with WdTempDir(bundle.wdversion, delete_on_exit=False) as d:
            self.write_lcin(bundle, d)
            proc = subprocess.Popen([self.executable], cwd=d,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            outs, errs = proc.communicate()
            errors = re.search(r'error:\s*(.*)', errs)
            if errors:
                raise RuntimeError('lc error: ' + errors.groups()[0])
        return self.collect(d)
        # print (errs)
        # print (d)

    def write_lcin(self, bundle, directory, filename='lcin.active'):
        w = Writer_lcin(filepath=os.path.join(directory, filename), bundle=bundle)
        w.write()

    def collect(self, directory, files=None):
        if files is None:
            files = ['light', 'veloc', 'spect', 'relat', 'image']
        ret = {}
        for f in files:
            try:
                ret[f] = self.collet_file(directory=directory, filename=f+'.dat')
            except IOError:
                pass
        return ret

    def collet_file(self, directory, filename):
        filepath = os.path.join(directory, filename)
        if filename == 'light.dat':
            return Reader_light(filepath).df
        elif filename == 'veloc.dat':
            return Reader_veloc(filepath).df
        return None

