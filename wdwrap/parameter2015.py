# coding=utf-8
from .parameter2007 import *


# First line:
# ... KSPEV,KSPOT,NOMAX,IFCGS,KTSTEP

class KSPEV(IntParameter):
    """Controls whether spots age (grow and decay) in radius. Currently there is no aging in spot temperature.
    Set KSPEV=0 for no aging, KSPEV=1 for aging.
    Solutions for spot aging need good starting estimates for spot parameters and careful monitoring
    of solution progress"""
    help_str = 'spots aging'
    min, max = 0, 1
    help_val = {0: 'no', 1: 'yes'}
    fmt_lcin = FortranFormatter('i', 1)
    flags = ParFlag.lc | ParFlag.dc

class KSPOT(IntParameter):
    """Controls whether the old simple spot algorithm (KSPOT=1) or the much more precise Vector
    Fractional Area algorithm (Wilson 2012b) for KSPOT=2 is applied."""
    help_str = 'spots algorithm'
    min, max = 1, 2
    help_val = {1: 'simple', 2: 'new 2012'}
    fmt_lcin = FortranFormatter('i', 1)
    flags = ParFlag.lc | ParFlag.dc

class NOMAX(IntParameter):
    """Setting NOMAX=1 eliminates the interval of constant size that otherwise exists at spot maximum
    (spot aging profiles then become triangular). Spot aging profiles are trepezoidal for NOMAX=0"""
    help_str = 'eliminate spots constant intervals'
    min, max = 0, 1
    help_val = {0: 'no', 1: 'yes'}
    fmt_lcin = FortranFormatter('i', 1)
    flags = ParFlag.lc | ParFlag.dc

class IFCGS(IntParameter):
    """Flux scale. IFCGS=0 Conventional solution in arbitrarily scaled flux,
    IFCGS=1 for an absolute solution with flux unit erg s^−1 cm^−3. DPCLOG needed."""
    help_str = 'eliminate spots constant intervals'
    min, max = 0, 1
    help_val = {0: 'arbitrary', 1: 'cgs'}
    fmt_lcin = FortranFormatter('i', 1)
    flags = ParFlag.lc | ParFlag.dc

class KTSTEP(IntParameter):
    """Positive integer that steps computed superior and inferior conjunction times by KTSTEP whole orbit cycles.
    Entered only with MPAGE=6. If KTSTEP=0, output is timing residuals instead of conjunction times."""
    help_str = ''
    min = 0
    fmt_lcin = FortranFormatter('i', 6)
    flags = ParFlag.lc | ParFlag.dc


#  Line 2
DPDT.fmt_lcin = FortranFormatter('d', 13, 6, flags=Flags.NOZERO)  # F.d14_6
PSHIFT.fmt_lcin = FortranFormatter('f', 9, 4, flags=Flags.ZERO | Flags.SIGN)  # F.f10_4

class DELPH(FloatParameter):
    """The duration of a light curve observation (assumed to be the same for all observations)
    for phase smearing computations as a decimal fraction the orbit period
    """
    help_str = 'light curve exp time (in period)'
    min, max = 0, 1
    fmt_lcin = FortranFormatter('f', 7, 5)
    flags = ParFlag.lc | ParFlag.dc

class NGA(IntParameter):
    """Number of Gaussian abscissas in the Gaussian quadrature of time/phase smearing.
    With NGA=1 there is no phase smearing. LC and DC allow NGA to be as small as 2 and as large as 10.
    There is no radial velocity smearing as of now, although that may soon be added."""
    help_str = 'number of Gaussian abscissas in time/phase smearing'
    min, max = 1, 10
    fmt_lcin = FortranFormatter('i', 2)
    flags = ParFlag.lc | ParFlag.dc


STDEV.fmt_lcin = FortranFormatter('d', 10, 4, flags=Flags.NOZERO)  # F.d11_4


#  Line 3
#  ..., phobs,lsp,tobs :: f10.4,i2,f8.4

class PHOBS(FloatParameter):
    """(Ph Obs): Phase at which a spectroscopic temperature was estimated (for use in a possible side computation
    to convert directly estimated temperature to flux-weighted mean surface temperature)"""
    help_str = 'Phase of spectroscopic temperature'
    min, max = 0, 1
    fmt_lcin = FortranFormatter('f', 9, 4)
    flags = ParFlag.lc | ParFlag.dc

class LSP(IntParameter):
    """Tells whether TOBS is for star 1 or star 2"""
    help_str = 'Star of TOBS'
    min, max = 1, 2
    fmt_lcin = FortranFormatter('i', 1)
    flags = ParFlag.lc | ParFlag.dc

class TOBS(FloatParameter):
    """(Tobs): Spectroscopic temperature at phase PHOBS"""
    help_str = 'Spectroscopic temperature'
    min, max = 0, 10
    unit = u.Unit('10000 K')
    fmt_lcin = FortranFormatter('f', 7, 4)
    flags = ParFlag.lc | ParFlag.dc


#  Line 4

THE.fmt_lcin = FortranFormatter('f', 7, 5, flags=Flags.NOZERO)
DPERDT.fmt_lcin = FortranFormatter('d', 13, 6, flags=Flags.NOZERO | Flags.SIGN)  # F.d12_5

#  Line 5
#  ..., ,fspot1,fspot2 :: 2f10.4

class FSPOT_(FloatParameter):
    min, max = 0, 1e4
    fmt_lcin = FortranFormatter('f', 9, 4)
    flags = ParFlag.lc | ParFlag.dc

class FSPOT1(FSPOT_):
    """Spot angular drift rates in longitude for star 1. Rate
    1.0000 means that drift just matches the mean orbital angular rate."""
    help_str = 'Spot drift os star 1'

class FSPOT2(FSPOT_):
    """Spot angular drift rates in longitude for star 2. Rate
    1.0000 means that drift just matches the mean orbital angular rate."""
    help_str = 'Spot drift os star 2'


#  Line 6
#   ..., dpclog :: f8.5

class DPCLOG(FloatParameter):
    """Logarithm (base 10) of distance (d) in parsecs."""
    help_str = 'log distance [parsec]'
    min, max = 0, 10
    fmt_lcin = FortranFormatter('f', 7, 5)
    flags = ParFlag.fittable | ParFlag.lc | ParFlag.dc


#  Line 7
#  Line 8
#  ...,  aextinc,calib  ::
#  < FORMAT(i3,2d13.5,4F7.3, F8.4  ,d10.4,F8.3,F8.4, f9.6)
#  > FORMAT(i3,2d13.6,4F7.3, d12.4 ,d11.4,F8.3,F8.4, f10.6, f8.4,d12.5)

class IBAND(IBANDbase):
    """Bands, band identification numbers (IBAND).
    Response curves for bands 86 to 91 are rectangular, have widths of 20 nm and are centered on the wavelength (in nm)
    indicated by their names."""
    fmt_lcin = FortranFormatter('i', 3)  # F.i3
    help_str = 'Band'
    min, max = 1, 95
    help_val = {
        1: 'Stromgren u', 2: 'Stromgren v', 3: 'Stromgren b', 4: 'Stromgren y',
        5: 'Johnson U', 6: 'Johnson B', 7: 'Johnson V',
        8: 'Johnson R', 9: 'Johnson I', 10: 'Johnson J', 11: 'Johnson K', 12: 'Johnson L', 13: 'Johnson M', 14: 'Johnson N',
        15: 'Cousins Rc', 16: 'Cousins Ic',
        17: 'Bessel90 UX', 18: 'Bessel90 BX', 19: 'Bessel90 B', 20: 'Bessel90 V', 21: 'Bessel90 R', 22: 'Bessel90 I',
        23: 'Tycho Bt', 24: 'Tycho Vt', 25: 'HIP', 26: 'KEP', 27: 'COROT SIS', 28: 'COROT EXO',
        29: 'Geneva U', 30: 'Geneva B', 31: 'Geneva B1', 32: 'Geneva B2', 33: 'Geneva V', 34: 'Geneva V1', 35: 'Geneva G',
        36: 'Vilnius U', 37: 'Vilnius P', 38: 'Vilnius X', 39: 'Vilnius Y', 40: 'Vilnius Z', 41: 'Vilnius V', 42: 'Vilnius S',
        43: 'Milone iz', 44: 'Milone iJ', 45: 'Milone iH', 46: 'Milone iK',
        47: 'YMS94 iz', 48: 'YMS94 iJ', 49: 'YMS94 iH', 50: 'YMS94 iK',
        51: 'YMS94 iL', 52: 'YMS94 iL\'', 53: 'YMS94 iM', 54: 'YMS94 in', 55: 'YMS94 iN',
        56: 'Solan DSS u\'', 57: 'Solan DSS g\'', 58: 'Solan DSS r\'', 59: 'Solan DSS i\'', 60: 'Solan DSS z\'',
        61: 'HST STIS Lyα', 62: 'HST STIS Fclear', 63: 'HST STIS Fsrf2', 64: 'HST STIS Fqtz',
        65: 'HST STIS C III', 66: 'HST STIS Mg II', 67: 'HST STIS Nclear', 68: 'HST STIS LNsrf2yα', 69: 'HST STIS Nqtz',
        70: 'HST STIS cn182', 71: 'HST STIS cn270',
        72: 'HST STIS Oclear', 73: 'HST STIS Oclear-lp', 74: 'HST STIS [O II]', 75: 'HST STIS [O III]',
        76: '2MASS J', 77: '2MASS H', 78: '2MASS Ks', 79: 'SWASP', 80: 'MOST',
        81: 'GAIA2006 G', 82: 'GAIA G', 83: 'GAIA GBP', 84: 'GAIA GRP', 85: 'GAIA GRVS',
        86: 'Milone  230', 87: 'Milone  250', 88: 'Milone  270', 89: 'Milone  290', 90: 'Milone  310', 91: 'Milone  330',
        92: 'Ca II triplet 858', 93: 'WIRE V+R', 94: 'LUT'
    }
    flags = ParFlag.outputspec | ParFlag.lc | ParFlag.curvedep


HLUM.fmt_lcin = FortranFormatter('d', 12, 6)
CLUM.fmt_lcin = FortranFormatter('d', 12, 6)
EL3.fmt_lcin = FortranFormatter('d', 11, 4, Flags.ZERO)
OPSF.fmt_lcin = FortranFormatter('d', 10, 4)
WL.fmt_lcin = FortranFormatter('f', 9, 6, Flags.ZERO)

class AEXTINC(FloatParameter):
    """Interstellar extinction (Aband in magnitude) in the designated photometric band.
    AEXTINC refers to a definite photometric band (the band designated by control integer LINKEXT),
    so it has only one value and it is not band-dependent"""
    help_str = 'extinction'
    unit = u.mag
    min = 0, 1e2
    fmt_lcin = FortranFormatter('f', 7, 4)
    flags = ParFlag.fittable | ParFlag.lc | ParFlag.dc

class CALIB(FloatParameter):
    """Flux calibration constant in erg s−1 cm−3 for a star of magnitude 0.00.
    It is an array in DC and a single quantity in LC.
    Table 3 on page 53 lists bands that have CALIB values determined and published."""
    help_str = 'flux calibration'
    min,max = 0, 100
    fmt_lcin = FortranFormatter('d', 11, 5)
    flags = ParFlag.lc | ParFlag.dc | ParFlag.curvedep

#  LINE 9+ spots
#  tstart(kp,i),tmax1(kp,i),tmax2(kp,i),tfinal(kp,i)
#  <    85 FORMAT(4f9.5)
#  >    85 FORMAT(4f9.5,4f14.5)

class TSTART(FloatParameter):
    help_str = 'spot parameter'
    fmt_lcin = FortranFormatter('f', 13, 5, Flags.ZERO)
    flags = ParFlag.lc | ParFlag.dc


class TMAX1(FloatParameter):
    help_str = 'spot parameter'
    fmt_lcin = FortranFormatter('f', 13, 5, Flags.ZERO)
    flags = ParFlag.lc | ParFlag.dc


class TMAX2(FloatParameter):
    help_str = 'spot parameter'
    fmt_lcin = FortranFormatter('f', 13, 5, Flags.ZERO)
    flags = ParFlag.lc | ParFlag.dc


class TFINAL(FloatParameter):
    help_str = 'spot parameter'
    fmt_lcin = FortranFormatter('f', 13, 5, Flags.ZERO)
    flags = ParFlag.lc | ParFlag.dc


