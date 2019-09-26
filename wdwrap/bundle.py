# coding=utf-8
from os import path
from wdwrap.parameters import ParameterSet
from io import Reader_lcin

from .config import default_cfg



wd_files = {
    '2007': {
        'lcin': """
            MPAGE,NREF,MREF,IFSMV1,IFSMV2,ICOR1,ICOR2,IF3B,LD1,LD2
            JDPHS,HJD0,PERIOD,DPDT,PSHIFT,STDEV,NOISE,SEED
            HJDST,HJDSP,HJDIN,PHSTRT,PHSTOP,PHIN,PHN
            MODE,IPB,IFAT1,IFAT2,N1,N2,PERR0,DPERDT,THE,VUNIT  
            E,A,F1,F2,VGA,XINCL,GR1,GR2,ABUNIN
            TAVH,TAVC,ALB1,ALB2,POTH,POTC,RM,XBOL1,XBOL2,YBOL1,YBOL2
            A3B,P3B,XINC3B,E3B,PERR3B,TC3B  # values have no effect when IF3B=0
            IBAND,HLUM,CLUM,XH,XC,YH,YC,EL3,OPSF,ZERO,FACTOR,WL
            
            BINWM1,SC1,SL1,NF1      # star 1 line profile parameters, for MPAGE=3 only
            WLL1,EWID1,DEPTH1,KKS1  # star 1 line profile parameters, for MPAGE=3 only  xn
            BINWM2,SC2,SL2,NF2      # star 2 line profile parameters, for MPAGE=3 only
            WLL2,EWID2,DEPTH2,KKS2  # star 2 line profile parameters, for MPAGE=3 only  xn
            
            XLAT,XLONG,RADSP,TEMSP  # spot parameters x2
            
            XCL,YCL,ZCL,RCL,OP1,FCL,EDENS,XMUE,ENCL # cloud parameters    xn                    
        """,
    }
}


class Bundle(ParameterSet):
    def __init__(self, wdversion='2007'):
        super(Bundle, self).__init__()
        self.wdversion = wdversion


    @classmethod
    def default_binary(cls, default_file=None, bundleno=0):
        if default_file is None:
            default_file = 'lcin_original.active'
        b = cls.open(Reader_lcin.default_wd_file_abspath(default_file), bundleno=bundleno)
        return b

    @classmethod
    def open(cls, filepath, bundleno=0):
        reader = Reader_lcin(filepath)
        return reader.bundles[bundleno]

    def __repr__(self):
        return '\n'.join([
            ' '.join([repr(v) for v in l.values()])
            for l in self.lines
        ])

    def __hash__(self):
        return hash(repr(self))





