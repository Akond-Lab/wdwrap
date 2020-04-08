#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

from itertools import chain

class FileStructure(object):
    _instance = None  # singlethon

    wd_files = {
        '2007': {
            'lcin': """
                MPAGE,NREF,MREF,IFSMV1,IFSMV2,ICOR1,ICOR2,IF3B,LD1,LD2
                JDPHS,HJD0,PERIOD,DPDT,PSHIFT,STDEV,NOISE,SEED
                HJDST,HJDSP,HJDIN,PHSTRT,PHSTOP,PHIN,PHN
                MODE,IPB,IFAT1,IFAT2,N1,N2,PERR0,DPERDT,THE,VUNIT  
                E,A,F1,F2,VGA,XINCL,GR1,GR2,ABUNIN
                TAVH,TAVC,ALB1,ALB2,POTH,POTC,RM,XBOL1,XBOL2,YBOL1,YBOL2
                A3B,P3B,XINC3B,E3B,PERR3B,TCONJ3B  # values have no effect when IF3B=0
                IBAND,HLUM,CLUM,XH,XC,YH,YC,EL3,OPSF,ZERO,FACTOR,WL

                BINWM1,SC1,SL1,NF1      #8  star 1 line profile parameters, for MPAGE=3 only
                WLL,EWID,DEPTH,KKS      #9  star 1 line profile parameters, for MPAGE=3 only  xn
                BINWM2,SC2,SL2,NF2      #10 star 2 line profile parameters, for MPAGE=3 only
                WLL,EWID,DEPTH,KKS      #11 star 2 line profile parameters, for MPAGE=3 only  xn

                XLAT,XLONG,RADSP,TEMSP  #12 spot parameters x2

                XCL,YCL,ZCL,RCL,OP1,FCL,EDENS,XMUE,ENCL #13 cloud parameters    xn                    
            """,
        },
        '2015': {
            'lcin': """
                MPAGE,NREF,MREF,IFSMV1,IFSMV2,ICOR1,ICOR2,IF3B,LD1,LD2,KSPEV,KSPOT,NOMAX,IFCGS,KTSTEP
                JDPHS,HJD0,PERIOD,DPDT,PSHIFT,DELPH,NGA,STDEV,NOISE,SEED
                HJDST,HJDSP,HJDIN,PHSTRT,PHSTOP,PHIN,PHN,PHOBS,LSP,TOBS
                MODE,IPB,IFAT1,IFAT2,N1,N2,PERR0,DPERDT,THE,VUNIT  
                E,A,F1,F2,VGA,XINCL,GR1,GR2,ABUNIN,FSPOT1,FSPOT2
                TAVH,TAVC,ALB1,ALB2,POTH,POTC,RM,XBOL1,XBOL2,YBOL1,YBOL2,DPCLOG
                A3B,P3B,XINC3B,E3B,PERR3B,TCONJ3B  # values have no effect when IF3B=0
                IBAND,HLUM,CLUM,XH,XC,YH,YC,EL3,OPSF,ZERO,FACTOR,WL,AEXTINC,CALIB

                BINWM1,SC1,SL1,NF1      # star 1 line profile parameters, for MPAGE=3 only
                WLL,EWID,DEPTH,KKS  # star 1 line profile parameters, for MPAGE=3 only  xn
                BINWM2,SC2,SL2,NF2      # star 2 line profile parameters, for MPAGE=3 only
                WLL,EWID,DEPTH,KKS  # star 2 line profile parameters, for MPAGE=3 only  xn

                XLAT,XLONG,RADSP,TEMSP,TSTART,TMAX1,TMAX2,TFINAL  # spot parameters x2

                XCL,YCL,ZCL,RCL,OP1,FCL,EDENS,XMUE,ENCL # cloud parameters    xn                    
            """,
        }
    }

    def __init__(self) -> None:
        super().__init__()
        self._structure = None
        self.parse_wd_files()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def line_classes_list(cls, filetype, version, line_no=None):
        return cls.get_instance().line_classes_list_(filetype, version, line_no=line_no)

    def line_classes_list_(self, filetype, version, line_no=None):
        try:
            iter(line_no)
        except TypeError:
            if line_no is None:
                line_no = range(len(self._structure[version][filetype]))
            else:
                line_no = [line_no]
        flattener = chain.from_iterable  # list of lists -> single list
        select = [self._structure[version][filetype][l] for l in line_no]
        ret = list(flattener(select))
        return ret

    def parse_wd_files(self):
        import importlib
        p = importlib.import_module('...drivers', __name__)
#        from .. import drivers as p
        self._structure = {}
        for ver, files in self.wd_files.items():
            ver_files = {}
            for filetype, filelines in files.items():
                lines = []
                for line in filelines.splitlines():
                    line = line.partition('#')[0]  # strip comments
                    nameslist = [s.strip() for s in line.split(',') if len(s.strip()) > 0]
                    classlist = [getattr(p, class_name) for class_name in nameslist]
                    if len(classlist) > 0:
                        lines.append(classlist)
                ver_files[filetype] = lines
            self._structure[ver] = ver_files

