from __future__ import print_function
import os
import re
import subprocess
from datetime import datetime, timedelta

from .tempdir import WdTempDir
from .io import *
from .config import cfg


class Runner(object):
    """Stateless Runner

    Thread safe, multiple jobs can be run be runner. Runner does not store state of the runner.
    """
    def __init__(self):
        super(Runner, self).__init__()

    def __call__(self, bundle, timeout=None):
        # TODO: super slow temp:
        import time
        # time.sleep(5)
        return self.run(bundle=bundle, timeout=timeout)

    def run(self, bundle, timeout=None):
        raise NotImplementedError

    def cancel(self, proc):
        self.canceled = True
        try:
            self.proc.kill()
            logging.getLogger('runner').info(f'Canceling job. Killing')
        except AttributeError:
            pass


class LcRunner(Runner):

    def __init__(self):
        super(LcRunner, self).__init__()
        self.executable = cfg().get('executables', 'lc')

    def run(self, bundle, timeout=None):
        # if timeout is None:
        #     timeout = 3075840000  # sto lat sto lat!
        # abs_timeout = datetime.now() + timedelta(seconds=timeout)
        # if datetime.now() > abs_timeout:
        #     raise TimeoutError

        with WdTempDir(bundle.wdversion, delete_on_exit=False) as d:
            self.write_lcin(bundle, d)
            proc = subprocess.Popen([self.executable], cwd=d,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            try:
                outs, errs = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                logging.getLogger('runner').info(f'Timeout ({timeout}s) occurred. Killing')
                proc.kill()
                raise TimeoutError

            errors = re.search(r'error:\s*(.*)', errs)
            if errors:
                raise RuntimeError('lc error: ' + errors.groups()[0])
            ret = self.collect(d)
        return ret
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

