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

class LcRunner(object):

    def __init__(self):
        super(LcRunner, self).__init__()
        self.executable = cfg().get('executables', 'lc')

    def run(self, bundle):
        with WdTempDir(delete_on_exit=False) as d:
            self.write_lcin(bundle, d)
            proc = subprocess.Popen([self.executable], cwd=d,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            outs, errs = proc.communicate()
            errors = re.search(r'error:\s*(.*)', errs)
            if errors:
                raise RuntimeError('lc error: ' + errors.groups()[0])
            self.collect(d, bundle)
            # print (errs)
            # print (d)

    def write_lcin(self, bundle, directory, filename='lcin.active'):
        w = Writer_lcin(filepath=os.path.join(directory, filename), bundle=bundle)
        w.write()

    def collect(self, directory, bundle, files=None):
        if files is None:
            files = ['light.dat', 'veloc.dat', 'spect.dat', 'relat.dat', 'image.dat']
        for f in files:
            try:
                self.collet_file(directory=directory, filename=f, bundle=bundle)
            except IOError:
                pass

    def collet_file(self, directory, filename, bundle):
        filepath = os.path.join(directory, filename)
        if filename == 'light.dat':
            bundle.light = Reader_light(filepath).table
        elif filename == 'veloc.dat':
            bundle.veloc = Reader_veloc(filepath).table

