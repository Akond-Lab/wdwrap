#  Copyright (c) 2020. Mikolaj Kaluszynski (et al.)  - CAMK, AkondLab

from ..config import cfg

try:
    wdver = str(cfg().get('executables', 'version'))
except Exception:
    wdver = '2007'

if wdver == '2007':
    from ..parameter2007 import *
elif wdver == '2015':
    from ..parameter2015 import *


