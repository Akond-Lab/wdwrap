# coding=utf-8

import re
import astropy.units as u

u_Rsol = u.Unit("6.95660e5 km")


class Formatter(object):

    def __init__(self, fmt=None, fixlen=None):
        super(Formatter, self).__init__()
        if fmt:
            self.fmt = fmt
        else:
            self.fmt = '{}'
        self.fixlen = fixlen

    def format(self, val):
        return self.fmt.format(val)

class FortranZFormatter(Formatter):
    """used FORTRAN formatting without leading zero e.g. f4.3: .123 instead of 0.123"""
    def format(self, val):
        s = super(FortranZFormatter, self).format(val)
        if self.fixlen and len(s) > self.fixlen:
            s = re.sub('0\.', '.', s)
        return s

class FortranDFormatter(FortranZFormatter):
    """used FORTRAN formatting had letter 'd' as exponential delimiter"""
    def format(self, val):
        return super(FortranDFormatter, self).format(val).replace('e', 'd')

class F:
    """Namespace to encapsulate FORTRAN formatters"""

    i1 = Formatter('{:1d}', 1)
    x1i1 = Formatter(' {:1d}', 2)
    i2 = Formatter('{:02d}', 2)
    x1i2 = Formatter(' {:02d}', 3)
    is2 = Formatter('{:+2d}', 2)
    x1is2 = Formatter(' {:+2d}',3)
    i3 = Formatter(' {:02d}', 3)
    i4 = Formatter(' {:03d}', 4)
    i5 = Formatter(' {:04d}', 5)

    f17_8 = FortranZFormatter(' {:016.8f}', 17)
    f15_6 = FortranZFormatter(' {:014.6f}', 15)
    f14_6 = FortranZFormatter(' {:013.6f}', 14)
    f13_6 = FortranZFormatter(' {:012.6f}', 13)
    f12_6 = FortranZFormatter(' {:011.6f}', 12)
    f11_5 = FortranZFormatter(' {:010.5f}', 11)
    f11_0 = FortranZFormatter(' {:09.0f}.', 11)
    f10_7 = FortranZFormatter(' {:09.7f}', 10)
    f10_6 = FortranZFormatter(' {:09.6f}', 10)
    f10_5 = FortranZFormatter(' {:09.5f}', 10)
    f10_4 = FortranZFormatter(' {:09.4f}', 10)
    f9_6  = FortranZFormatter(' {:08.6f}', 9)
    f9_5  = FortranZFormatter(' {:08.5f}', 9)
    f9_4  = FortranZFormatter(' {:08.4f}', 9)
    f9_3  = FortranZFormatter(' {:08.3f}', 9)
    f9_2  = FortranZFormatter(' {:08.2f}', 9)
    f8_4  = FortranZFormatter(' {:07.4f}', 8)
    f8_3  = FortranZFormatter(' {:07.4f}', 8)
    f8_2  = FortranZFormatter(' {:07.2f}', 8)
    f7_5  = FortranZFormatter(' {:06.5f}', 7)
    f7_4  = FortranZFormatter(' {:06.4f}', 7)
    f7_3  = FortranZFormatter(' {:06.3f}', 7)
    f7_2  = FortranZFormatter(' {:06.2f}', 7)
    f6_5  = FortranZFormatter('{:6.5f}', 6)

    d17_10 = FortranDFormatter(' {:16.10e}', 17)
    d14_7 =  FortranDFormatter(' {:13.7e}', 14)
    d13_6 =  FortranDFormatter(' {:12.6e}', 13)
    d13_5 =  FortranDFormatter(' {:12.5e}', 13)
    d12_6 =  FortranDFormatter(' {:11.6e}', 12)
    d12_5 =  FortranDFormatter(' {:11.5e}', 12)
    d11_5 =  FortranDFormatter(' {:10.5e}', 11)
    d11_4 =  FortranDFormatter(' {:10.4e}', 11)
    d11_3 =  FortranDFormatter(' {:10.3e}', 11)
    d10_4 =  FortranDFormatter(' {:9.4e}', 10)


class Parameter(object):
    format_str = '{}'
    fmt_lcin = '{}'
    help_str = 'parameter'
    help_val = None
    max = None
    min = None
    unit = None
    nan_value = None

    def __init__(self, val=None):
        super(Parameter, self).__init__()
        if isinstance(val, str):
            self.from_str(val)
        else:
            self.val = val
        self.fix = True

    def __str__(self):
        return self.format_str.format(self.val)

    def __repr__(self):
        if self.fix:
            return '{:s}={:s}'.format(self.name(), self)
        else:
            return '*{:s}={:s}'.format(self.name(), self)

    def format(self, val, fmt):
        return fmt.format(val)

    def isnan(self):
        return self.val == self.nan_value

    def from_str(self, val):
        raise NotImplementedError('from_str method should be overridden')

    @property
    def lcin(self):
        return self.format(self.val, self.fmt_lcin)

    @property
    def doc(self):
        return self.__doc__

    @classmethod
    def name(cls):
        return cls.__name__

class FloatParameter(Parameter):
    def __float__(self):
        return float(self.val)

    def from_str(self, val):
        self.val = float(re.sub('[dD]', 'e', val, 1))


class IntParameter(Parameter):
    def __int__(self):
        return int(self.val)

    def from_str(self, val):
        self.val = int(val)


class MPAGE(IntParameter):
    """type of output produced by LC is determined by control integer MPAGE and can be light curves (MPAGE=1),
    radial velocity curves (MPAGE=2), spectral line profiles (MPAGE=3),
    relative star dimensions (MPAGE=4), or sky coordinates for producing images (MPAGE=5)."""
    help_str = 'type of output'
    min, max = 1, 5
    help_val = {1: 'light curves', 2: 'velocity curves', 3: 'line profiles', 4: 'radii vs. phase', 5: 'pictures'}
    fmt_lcin = F.i1
    nan_value = 9


class NREF(IntParameter):
    """If detailed reflection is selected (MREF=2), then NREF specifies the number of reflections in a multiple
    reflection effect. Set NREF=1 for 1 reflection from each star, NREF=2 for 2 reflections, etc.
    More reflections use more computing time. If MREF=1, the value of NREF is irrelevant."""
    help_str = 'number of reflections'
    min = 1
    fmt_lcin = F.x1i1


class MREF(IntParameter):
    """The reflection effect can be handled either in detail (viz. Wilson 1990) or by the inverse square law,
    with corrections for penumbral and ellipsoidal effects. The latter method is much faster and is adequate for many
    realistic situations. Set MREF=1 for the simple treatment and MREF=2 for the detailed treatment."""
    help_str = 'simple or detailed reflection'
    min, max = 1, 2
    help_val = {1: 'approximate', 2: 'detailed'}
    fmt_lcin = F.x1i1


class IFSMV_(IntParameter):
    min, max = 0, 1
    help_val = {0: 'fixed in longitude', 1: 'move in longitude'}
    fmt_lcin = F.x1i1


class IFSMV1(IFSMV_):
    """Tells, hether spots on stars 1 are to move in longitude due to asynchronous rotation and orbital eccentricity.
    If IFSMV1 is set to 0, the spots on star 1 remain at fixed longitudes, referenced to the line of centers
    of the two stars. This behavior is expected for hot spots due to an accretion stream.
    If IFSMV1=1 and the star rotates asynchronously, then the spots on star 1 follow the physical surface as time progresses.
    This behavior is expected for magnetic spots. In both cases, there is no motion in latitude."""
    help_str = 'allow move of star 1 spots in longitude'


class IFSMV2(IFSMV_):
    """Tells, hether spots on stars 2 are to move in longitude due to asynchronous rotation and orbital eccentricity.
    If IFSMV2 is set to 0, the spots on star 2 remain at fixed longitudes, referenced to the line of centers
    of the two stars. This behavior is expected for hot spots due to an accretion stream.
    If IFSMV2=1 and the star rotates asynchronously, then the spots on star 2 follow the physical surface as time progresses.
    This behavior is expected for magnetic spots. In both cases, there is no motion in latitude."""
    help_str = 'allow move of star 2 spots in longitude'


class ICOR_(IntParameter):
    help_str = 'RV proximity corrections'
    min, max = 0, 1
    help_val = {0: 'not apply', 1: 'apply'}
    fmt_lcin = F.x1i1


class ICOR1(ICOR_):
    """These integers refer to proximity and eclipse effects on radial velocities for star 1.
    Value 0 turns the effects off, 1 turns them on"""


class ICOR2(ICOR_):
    """These integers refer to proximity and eclipse effects on radial velocities for star 2.
    Value 0 turns the effects off, 1 turns them on"""


class IF3B(IntParameter):
    """This control integer tells the program if there is a third body (IF3B=1) or not (IF3B=0)"""
    help_str = 'third body'
    min, max = 0, 1
    help_val = {0: 'ignore third body parameters', 1: 'utilize third body parameters'}
    fmt_lcin = F.x1i1


class LD_(IntParameter):
    help_str = 'limb darkening law'
    min, max = -3, 3
    help_val = {
        +1: 'fixed linear cosine law', +2: 'fixed log law', +3: 'fixed square root law',
        -1: 'computed linear cosine law', -2: 'computed log law', -3: 'computed square root law',
    }
    fmt_lcin = F.x1is2


class LD1(LD_):
    """These integers set the limb darkening laws for star 1.
    LD1=±1 for the linear cosine law, LD1=±2 for a logarithmic law, and LD1=±3 for a square root law.
    For positive LD1, the x, y coefficients are fixed and equal to the input values.
    For negative LD’s, subroutine LIMDARK ignores the input [x,y] and computes x,y coefficients locally
    in terms of Teff, logg and [M/H]."""


class LD2(LD_):
    """These integers set the limb darkening laws for star 2.
    LD2=±1 for the linear cosine law, LD2=±2 for a logarithmic law, and LD2=±3 for a square root law.
    For positive LD2, the x, y coefficients are fixed and equal to the input values.
    For negative LD’s, subroutine LIMDARK ignores the input [x,y] and computes x,y coefficients locally
    in terms of Teff, logg and [M/H]."""

class JDPHS(IntParameter):
    """This is 1 if the independent variable is time and 2 if it is phase. Setting JDPHS=1 in LC causes time
    (ordinarily Heliocentric Julian Date) to be stepped from HJDST to HJDSP in uniform intervals of length HJDIN.
    Phases for those times are computed according to the supplied ephemeris, including the effect of dP/dt.
    Setting JDPHS=2 in LC causes phase to be stepped from PHSTRT to PHSTOP in uniform intervals of length PHIN.
    Times for those phases are computed according to the supplied ephemeris, again including the effect of dP/dt.
    Regardless of whether JDPHS is 1 or 2, mutually consistent time and phase are listed in the output
    (columns 1 and 2, respectively).
    At present, the ephemeris includes only the initial epoch (t0), the period at that epoch (P0),
    and the first time derivative of the period, dP/dt."""
    help_str = 'time or phase independent variable'
    min, max = 1, 2
    help_val = {1: 'time', 2: 'phase'}
    fmt_lcin = F.i1

class HJD0(FloatParameter):
    """(t0) This is the zero point of the orbital ephemeris. Usually one uses Heliocentric Julian Date,
    although that is only a convention and any consistent system of time can be used."""
    help_str = 't0 zero point of the orbital ephemeris'
    unit = u.day
    fmt_lcin = F.f15_6


class PERIOD(FloatParameter):
    """(P0) The binary orbit period at the reference time t0, ordinarily in mean solar days. P0 affects radial velocity
    amplitudes and is used to compute phase from time (if JDPHS=1) and time from phase (if JDPHS=2).
    P0 can be adjusted only if JDPHS=1 and observation times (rather than phases) are entered."""
    help_str = 'P0 binary orbit period'
    unit = u.day
    min = 0.0
    fmt_lcin = F.d17_10


class DPDT(FloatParameter):
    """(dP/dt) The first time derivative of the orbital period. Second and higher derivatives arenot used.
    DPDT can be adjusted only if JDPHS=1 and observation times (rather than phases) are entered.
    This quantity is dimensionless."""
    help_str = 'dP/dt derivative of the orbital period'
    fmt_lcin = F.d13_6

class PSHIFT(FloatParameter):
    """(φ0) A constant shift applied to computed phases. Usually one enters +0.0000 for φ0, but it may be convenient  to shift the phases.
    For example, a phase shift of about half a cycle can effectively interchange the star labels (1 vs. 2) without altering the observational data.
    The main purpose of φ0 is to allow the DC program to adjust for a zero point error in the ephemeris used to compute the phases.
    The unit is the orbital period. One should not adjust both PSHIFT and HJD0 because they will be perfectly correlated."""
    help_str = 'φ0 phase shift'
    fmt_lcin = F.f10_6

class STDEV(FloatParameter):
    """Light curves with synthetic Gaussian noise can be produced by entering a non- zero value for the input quantity STDEV,
    which is labeled “fract. sd.” in the output. As the label suggests, STDEV is in the unit of the light
    at the reference phase (PHN).
    The way that the noise (scatter) scales with light level is controlled by input integer NOISE.
    Noise generation works the same way for radial velocities, except that there is no variation of the scatter with level.
    For velocity scatter, enter STDEV in the velocity unit (VUNIT)"""
    help_str = 'synthetic noise level'
    min = 0
    fmt_lcin = F.d10_4

class NOISE(IntParameter):
    """The way that the noise (scatter) scales with light level is controlled by input integer NOISE.
    Scatter is proportional to light level for NOISE=2, proportional to the square root of the light level for NOISE=1,
    and independent of light level for NOISE=0"""
    help_str = 'synthetic noise scaling'
    min = 0
    max = 2
    help_val = {0: 'no level-dependent weights', 1: 'scales with sqrt(level)', 2:'scales with level'}
    fmt_lcin = F.x1i1

class SEED(FloatParameter):
    """The random number generator needs a seed (FORTRAN name SEED), labeled “seed” in the output.
    SEED should be larger than 100000001. and smaller than twice that value.
    The procedure should work for other SEED’s, but one should stay within the mentioned range for best results."""
    help_str = 'random generator seed'
    min = 100000001.0
    max = 2.0 * min - 1.0
    fmt_lcin = F.f11_0

class HJDST(FloatParameter):
    """The time at which LC is to start computing output points. HJDST is utilized only if JDPHS=1."""
    help_str = 'output start time'
    unit = u.day
    fmt_lcin = F.f14_6

class HJDSP(FloatParameter):
    """The time at which LC is to stops computing output points. HJDSP is utilized only if JDPHS=1."""
    help_str = 'output stop time'
    unit = u.day
    fmt_lcin = F.f15_6

class HJDIN(FloatParameter):
    """The time increment for output points. HJDIN = 0.001 will produce output points spaced by 0.001 days."""
    help_str = 'output time increment'
    unit = u.day
    fmt_lcin = F.f13_6

class PHSTRT(FloatParameter):
    """The first phase at which output points are to be produced. PHSTOP should be larger than PHSTRT,
    but neither has to be int the range 0 to 1. For example, PHSTRT= −3.2000, PHSTOP = 27.4422 is a valid phase range.
    PHSTRT, PHSTOP, and the next quantity, PHIN, are utilized only if JDPHS=2"""
    help_str = 'output start phase'
    fmt_lcin = F.f12_6

class PHSTOP(FloatParameter):
    """The last phase at which output points are to be produced. PHSTOP should be larger than PHSTRT,
    but neither has to be int the range 0 to 1. For example, PHSTRT= −3.2000, PHSTOP = 27.4422 is a valid phase range.
    PHSTRT, PHSTOP, and the next quantity, PHIN, are utilized only if JDPHS=2"""
    help_str = 'output end phase'
    fmt_lcin = F.f12_6

class PHIN(FloatParameter):
    """The phase increment for output points. PHIN = 0.020 will produce output points every 0.020 in phase,
    within the range PHSTRT to PHSTOP. PHIN, are utilized only if JDPHS=2"""
    help_str = 'output phase increment'
    fmt_lcin = F.f12_6

class PHN(FloatParameter):
    """The phase of normalization, which is the phase at which the column of normalized light is normalized
    to the input value FACTOR and the magnitude column is caused to equal the magnitude zero point, whose name is ZERO."""
    help_str = 'phase normalization'
    fmt_lcin = F.f12_6

class MODE(IntParameter):
    """Modes of Program Operation (Solution Constraints) expressing functional relationship among parameters."""
    help_str = 'mode of operation'
    fmt_lcin = F.i2
    min = -1
    max = 6
    help_val = {
        -1: 'X-ray binaries',
        0: 'no constraints',
        1: 'overcontact binaries (W UMa) thermal contact',
        2: 'detached binaries, no constraints on the potentials',
        3: 'overcontact binaries geometrical contact',
        4: 'semi-detached binaries, star 1 filling its limiting lobe',
        5: 'semi-detached binaries, star 2 filling its limiting lobe (Algol type)',
        6: 'double contact binaries',
    }

class IPB(IntParameter):
    """Assign IPB=0 for normal MODE 1, 2, 3, 4, 5, or 6 operation in which star 2’s luminosity (L2) is to be computed
    from temperatures T1 and T2, the luminosity of star 1, and the radiation laws (as well as other information known
    by the program about system geometry, etc.).
    If you want to set L2 independently (perhaps because you have no trust in the radiation laws in a particular situation),
    set IPB=1 and the program will use the input L2 value.
    Modes 0 and −1 always accept the input L2, so they operate as if IPB=1."""
    help_str = 'independent L2'
    fmt_lcin = F.x1i1
    min = 0
    max = 1
    help_val = {
        0: 'L2 computed from T1 T2 L1',
        1: 'L2 set independently',
    }

class IFAT_(IntParameter):
    fmt_lcin = F.x1i1
    min = 0
    max = 1
    help_val = {
        0: 'blackbody',
        1: 'atmosphere',
    }

class IFAT1(IFAT_):
    """Control whether a blackbody or a stellar atmosphere formulation is used for local emission on star 1"""
    help_str = 'blackbody or atmosphere for star 1'

class IFAT2(IFAT_):
    """Control whether a blackbody or a stellar atmosphere formulation is used for local emission on star 2"""
    help_str = 'blackbody or atmosphere for star 2'

class N_(IntParameter):
    fmt_lcin = F.i4
    min = 2

class N1(N_):
    """Grid size integers for star 1. The number of latitude rows per hemisphere.
    The number of surface elements in longitude scales with N1 and scales approximately with the sine of the
    “latitude” coordinate, which runs from 0 at the “North” (+z) pole to π radians at the “South” (−z) pole."""
    help_str = 'grid size for star 1'

class N2(N_):
    """Grid size integers for star 2. The number of latitude rows per hemisphere.
    The number of surface elements in longitude scales with N2 and scales approximately with the sine of the
    “latitude” coordinate, which runs from 0 at the “North” (+z) pole to π radians at the “South” (−z) pole."""
    help_str = 'grid size for star 2'

class PERR0(FloatParameter):
    """(ω0): Initial argument of periastron for star 1. The argument of periastron for star 2 differs by π radians.
    PERR0 is ω at the reference time of the ephemeris t0. The program is written so that, as the argument of periastron
    changes, both eclipses have excursions in phase in the same way as a real binary.
    For circular orbits, the program ignores the input value and sets ω to π/2 radians."""
    help_str = 'ω0 initial periastron'
    fmt_lcin = F.f13_6
    unit = u.rad

class DPERDT(FloatParameter):
    """(dω/dt): The first time derivative of ω. DPERDT can be adjusted only if JDPHS=1 and observation times
    (rather than phases) are entered. The instantaneous argument of periastron is ω = ω0 + dω/dt (t − t0).
    The program does not consider any more complicated variations of ω.
    The unit is radians per adopted time unit (usually mean solar day)."""
    help_str = 'dω/dt derivative of the periastron'
    fmt_lcin = F.d12_5
    unit = u.rad / u.day

class THE(FloatParameter):
    """(φe) The semi-duration of primary eclipse in phase units (i.e. range 0 to 1 for a cycle).
    This parameter is used only in mode −1 and usually relates to binaries in which star 1 has negligible size compared to star 2.
    The idea is to fix φe according to X-ray eclipses of a neutron star, black hole, or white dwarf,
    and require the overall solution to be consistent with that value.
    Although mode −1 logic was originally intended for X-ray eclipses of compact objects, it also will work for optical
    eclipses of any star for which R1/R2 is extremely small, such as a main sequence star with a red giant companion.
    The orbit can be eccentric and rotation can be non-synchronous. Parameter φe is ignored in all other operation modes."""
    help_str = 'φe semi-duration of primary eclipse'
    min = 0.0
    max = 1.0
    fmt_lcin = F.f7_5

class VUNIT(FloatParameter):
    """Unit for radial velocity input and output, in km/sec. Usually it is a round number, such as 100 km/sec,
    of the order of the input velocities for DC"""
    help_str = 'RV unit [km/sec]'
    min = 0.0
    unit = u.km/u.s
    fmt_lcin = F.f8_2

class E(FloatParameter):
    """(e): Binary orbital eccentricity"""
    help_str = 'e eccentricity'
    min = 0
    fmt_lcin = F.f6_5

class A(FloatParameter):
    """(a): The length of the semi-major axis in solar radii (6.95660*10^5 km [Haberreiter+2008])
    of the relative orbital ellipse.
    It is the sum of the two absolute semi-major axes, so a = a1 + a2"""
    fmt_lcin = F.d13_6
    help_str = 'a semi-major axis [Rsun]'
    min = 0
    unit = u_Rsol

class F_(FloatParameter):
    fmt_lcin = F.f10_4

class F1(F_):
    """(F1): The ratio of the (constant) axial rotation rate to the mean orbital rate for star 1.
    The angular rotation is assumed to be uniform (not latitude dependent).
    Value unity represents synchronous rotation in a circular orbit.
    In eccentric cases it is expected that rotation will tend to synchronize to the periastron angular rate because
    of the strong dependence of the tide raising force on distance. Periastron-synchronized F is given by
            F=sqrt(􏰃1+e / (1−e)^3)
    The F’s affect star figures, surface brightnesses (through the gravity effect), limiting lobe sizes,
    and thus both light curves and radial velocities."""
    help_str = 'F1 star 1 axial to orbital rotation ratio'

class F2(F_):
    """(F2): The ratio of the (constant) axial rotation rate to the mean orbital rate for star 2.
    The angular rotation is assumed to be uniform (not latitude dependent).
    Value unity represents synchronous rotation in a circular orbit.
    In eccentric cases it is expected that rotation will tend to synchronize to the periastron angular rate because
    of the strong dependence of the tide raising force on distance. Periastron-synchronized F is given by
            F=sqrt(􏰃1+e / (1−e)^3)
    The F’s affect star figures, surface brightnesses (through the gravity effect), limiting lobe sizes,
    and thus both light curves and radial velocities."""
    help_str = 'F2 star 2 axial to orbital rotation ratio'


class VGA(FloatParameter):
    """(Vγ): The radial velocity of the (possibly multiple-system) barycenter in the unit VUNIT km/s.
    Vγ is assumed constant, although the EB center of mass radial velocity follows from motion about the barycenter
    if there is a third body."""
    help_str = 'Vγ barycenter radial velocity'
    fmt_lcin = F.f10_4


class XINCL(FloatParameter):
    """(i): The binary orbital inclination to the plane of the sky, in degrees.
    If the inclination is in the range 0 to 90◦, the binary orbits counter-clockwise as projected onto the plane of the sky,
    while above 90◦ it orbits clockwise, according to the program’s coordinate conventions.
    Those conventions were different prior to the revision of 1992."""
    help_str = 'i orbit inclination'
    fmt_lcin = F.f9_3
    min, max = 0.0, 180.0
    unit = u.deg

class GR_(FloatParameter):
    fmt_lcin = F.f7_3
    min, max = 0.0, 1.0


class GR1(GR_):
    """(g1): The exponent in the bolometric gravity brightening (a.k.a. darkening) law for star 1.
    Value 1.000 means that bolometric flux is proportional to local effective gravity,
    while 0.000 means that it is constant over the surface (ignoring other effects such as spots, reflection heating, etc.).
    The g’s are expected to be unity for radiative envelopes, while they should be smaller for convective envelopes,
    perhaps about 0.3. Some other programs use a gravity brightening exponent expressed in terms of effective temperature,
    for which the usual symbol is β. The quantities are related by g = 4β."""
    help_str = 'g1 star 1 exponent of the gravity brightening'

class GR2(GR_):
    """(g2): The exponent in the bolometric gravity brightening (a.k.a. darkening) law for star 2.
    Value 1.000 means that bolometric flux is proportional to local effective gravity,
    while 0.000 means that it is constant over the surface (ignoring other effects such as spots, reflection heating, etc.).
    The g’s are expected to be unity for radiative envelopes, while they should be smaller for convective envelopes,
    perhaps about 0.3. Some other programs use a gravity brightening exponent expressed in terms of effective temperature,
    for which the usual symbol is β. The quantities are related by g = 4β."""
    help_str = 'g2 star 2 exponent of the gravity brightening'


class ABUNIN(FloatParameter):
    """Chemical composition needs to be specified via input parameter ABUNIN.
    If ABUNIN is not one of the 19 Kurucz values, it is reset automatically to the nearest Kurucz value,
    as there is no interpolation in [M/H]"""
    help_str = 'metallicity [M/H]'
    fmt_lcin = F.f7_2


class TAV_(FloatParameter):
    fmt_lcin = F.f7_4
    unit = u.Unit('10000 K')

class TAVH(TAV_):
    """(T1): The mean surface effective temperature of star 1, not including re-radiation (reflection) or spots.
    The mean is weighted by the local bolometric flux. The program accepts T1 as model parameters and converts to local
    surface temperatures for internal computations.
    The conversion between mean and polar temperatures is made via Eqn. 8 of Wilson (1979), and the local surface
    temperatures are then computed from the polar temperatures and the gravity brightening law. The unit is 10,000 K."""
    help_str = 'T1 Teff of star 1'

class TAVC(TAV_):
    """(T2): The mean surface effective temperature of star 2, not including re-radiation (reflection) or spots.
    The mean is weighted by the local bolometric flux. The program accepts T1 as model parameters and converts to local
    surface temperatures for internal computations.
    The conversion between mean and polar temperatures is made via Eqn. 8 of Wilson (1979), and the local surface
    temperatures are then computed from the polar temperatures and the gravity brightening law. The unit is 10,000 K."""
    help_str = 'T1 Teff of star 2'

class ALB_(FloatParameter):
    fmt_lcin = F.f7_3
    min, max = 0.0, 1.0

class ALB1(ALB_):
    """(A1): The bolometric albedo for reflection heating and re-radiation on star 1.
    The bolometric albedo is the local ratio of re-radiated bolometric energy to received bolometric energy.
    It is assumed to be constant for each star.
    The expected value for radiative envelopes is 1.0, while for convective envelopes it should be perhaps 0.5,
    although observations sometimes indicate values between 0.5 and 1.0."""
    help_str = 'A1 albedo of star 1'

class ALB2(ALB_):
    """(A1): The bolometric albedo for reflection heating and re-radiation on star 2.
    The bolometric albedo is the local ratio of re-radiated bolometric energy to received bolometric energy.
    It is assumed to be constant for each star.
    The expected value for radiative envelopes is 1.0, while for convective envelopes it should be perhaps 0.5,
    although observations sometimes indicate values between 0.5 and 1.0."""
    help_str = 'A1 albedo of star 2'

class POT_(FloatParameter):
    fmt_lcin = F.d13_6

class POTH(POT_):
    """Modified surface ’potential’ for star 1."""
    help_str = 'Modified surface ’potential’ for star 1'

class POTC(POT_):
    """Modified surface ’potential’ for star 2."""
    help_str = 'Modified surface ’potential’ for star 2'

class RM(FloatParameter):
    """(q): The mass ratio of stars 2 and 1, m2/m1."""
    help_str = 'q mass ratio m2/m1'
    min = 0.0
    fmt_lcin = F.d13_6

class BOL_(FloatParameter):
    fmt_lcin = F.f7_3

class XBOL1(BOL_):
    """(xbol1): The coefficient of cos γ in the bolometric limb darkening law.
    They are used only in computation of “detailed” reflection (Wilson 1990), with MREF=2.
    See YBOL1, for the complete law and explanation."""
    help_str = 'star 1 x coefficient of limb darkening law'

class XBOL2(BOL_):
    """(xbol2): The coefficient of cos γ in the bolometric limb darkening law.
    They are used only in computation of “detailed” reflection (Wilson 1990), with MREF=2.
    See YBOL1, for the complete law and explanation."""
    help_str = 'star 2 x coefficient of limb darkening law'

class YBOL1(BOL_):
    """(ybol1): If control integer LD1(2)=+2 or −2, these are the coefficients of the cos γ ln(cos γ) term
    in the bolometric logarithmic limb darkening law. The complete logarithmic law is
        I/I0 = 1 − x + x cos(γ) − y cos(γ) ln(cos γ)
    which was advocated by Klinglesmith & Sobieski (1970).

    If LD1(2)=+3 or −3, they are the coeffi- cients of the bolometric square root law.
    The complete square root law (Diaz-Cordov ́es & Gim ́enez 1992) is
        I/I0 = 1 − x + x cos(γ) − y( 1 - sqrt(cos γ) )
    Coefficients for all these darkening laws have been tabulated by Van Hamme (1993).
    """
    help_str = 'star 1 y coefficient of limb darkening law'

class YBOL2(BOL_):
    """(ybol2): The coefficient in the bolometric limb darkening law.
    They are used only in computation of “detailed” reflection (Wilson 1990), with MREF=2.
    See YBOL1, for the complete law and explanation."""
    help_str = 'star 2 y coefficient of limb darkening law'


class A3B(FloatParameter):
    """(a3b): The length of the semi-major axis of the relative orbit of the EB center of mass around the system’s
    barycenter, in solar radii."""
    help_str = 'a3b semi-major of EB center around barycenter [Rsol]'
    fmt_lcin = F.d12_6
    unit = u_Rsol


class P3B(FloatParameter):
    """(P3b): The third body orbit period in mean solar days."""
    help_str = 'P3b third body period [day]'
    fmt_lcin = F.d14_7
    unit = u.day

class XINC3B(FloatParameter):
    """(i3b): The third body orbital inclination to the plane of the sky, in degrees.
    This parameter should not be adjusted if a3b is adjusted since a3b and i3b are perfectly correlated."""
    fmt_lcin = F.f11_5
    help_str = 'i3b third body inclination [deg]'
    unit = u.deg


class E3B(FloatParameter):
    """(e3b): Third body orbital eccentricity."""
    fmt_lcin = F.f9_6
    help_str = 'e3b third body eccentricity'
    min = 0


class PERR3B(FloatParameter):
    """(ω3b): Argument of periastron of third body orbit."""
    fmt_lcin = F.f10_7
    help_str = 'ω3b third body argument of periastron'
    unit = u.rad


class TCONJ3B(FloatParameter):
    """(tc3b): Time of superior conjunction of the EB center of mass with respect to the third body, usually in HJD"""
    fmt_lcin = F.f17_8
    help_str = 'tc3b superior conjunction of EB center with respect to the third body'
    unit = u.day

class IBAND(IntParameter):
    """Bands, band identification numbers (IBAND).
    Response curves for bands 17 to 22 are rectangular, have widths of 20 nm and are centered on the wavelength (in nm)
    indicated by their names."""
    fmt_lcin = F.i3
    help_str = 'Band'
    min, max = 1, 25
    help_val = {
        1: 'u', 2: 'v', 3: 'b', 4: 'y',
        5: 'U', 6: 'B', 7: 'V', 8: 'R', 9: 'I', 10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'Rc', 16: 'Ic',
        17: '230', 18: '250', 19: '270', 20: '290', 21: '310', 22: '330',
        23: 'TyB', 24: 'TyV', 25: 'HIP',
    }

class HLUM(FloatParameter):
    """Bandpass luminosity of star 1, used if  IPB = 1"""
    fmt_lcin = F.d13_5
    help_str = 'L1 luminosity of star 1'


class CLUM(FloatParameter):
    """Bandpass luminosity of star 2, used if  IPB = 1"""
    fmt_lcin = F.d13_5
    help_str = 'L1 luminosity of star 2'


class XH(FloatParameter):
    """Wavelength-specific limb darkening coefficient in the linear terms for star 1.
    The laws have the same forms as for bolometric limb darkening"""
    fmt_lcin = F.f7_3
    help_str = 'star 1 limb darkening coefficient x'


class XC(FloatParameter):
    """Wavelength-specific limb darkening coefficient in the linear terms for star 2.
    The laws have the same forms as for bolometric limb darkening"""
    fmt_lcin = F.f7_3
    help_str = 'star 2 limb darkening coefficient x'


class YH(FloatParameter):
    """Wavelength-specific limb darkening coefficient in the linear terms for star 1.
    The laws have the same forms as for bolometric limb darkening"""
    fmt_lcin = F.f7_3
    help_str = 'star 1 limb darkening coefficient y'


class YC(FloatParameter):
    """Wavelength-specific limb darkening coefficient in the linear terms for star 2.
    The laws have the same forms as for bolometric limb darkening"""
    fmt_lcin = F.f7_3
    help_str = 'star 2 limb darkening coefficient y'


class EL3(FloatParameter):
    """(l3): Third light. There is one value for each light curve, but of course no value for a radial velocity curve.
    The unit should be the total system light at a specified phase.
    For example, suppose l3 (program input-output value) for some particular light curve is 0.0500,
    the specified phase is chosen to be 0.2500, and the total system light produced by LC at phase 0.2500 is 1.0400.
    Then the number to be published for the l3 of that curve would be 0.0500 divided by 1.0400, or 0.0481."""
    fmt_lcin = F.f8_4
    help_str = 'l3 third light'


class OPSF(FloatParameter):
    fmt_lcin = F.d10_4
    help_str = ''


class ZERO(FloatParameter):
    """This is the reference level for output magnitudes (the magnitude at phase PHN)"""
    fmt_lcin = F.f8_3
    help_str = 'magnitude zero point'


class FACTOR(FloatParameter):
    """This is the scaling factor for the normalized light column.
    The number in that column will equal FACTOR at phase PHN"""
    fmt_lcin = F.f8_4
    help_str = 'normalized light scaling factor'


class WL(FloatParameter):
    """The observational wavelengths in microns of each light or velocity curve.
    Wavelengths need to be entered for velocity curves, although they have little effect on the output,
    and any wavelength somewhere near the spectral region of interest should be adequate.
    Wavelengths are no longer used for light curves, which now are based on integrated bandpass radiation.
    Wavelengths are still entered for use as reference wavelengths for line profiles and for opacity computations in
    circumstellar attenuation."""
    fmt_lcin = F.f9_6
    help_str = 'Reference wavelength'
    
class BINWM_(FloatParameter):
    fmt_lcin = F.f11_5
    unit = u.micron

class BINWM1(BINWM_):
    """Spectral. The bin width in microns. Too small a bin width gives noisy profiles.
    Too large a bin width gives insufficient spectral resolution."""
    min = 0
    help_str = 'Star 1. Spectral bin with'

class BINWM2(BINWM_):
    """Spectral. The bin width in microns. Too small a bin width gives noisy profiles.
    Too large a bin width gives insufficient spectral resolution."""
    help_str = 'Star 2. Spectral bin with'

class SC_(FloatParameter):
    fmt_lcin = F.f9_4

class SC1(SC_):
    """Spectral. The continuum scale (continuum flux at the reference wavelength). The unit is decided by the user."""
    help_str = 'Star 1. Spectral continuum scale'

class SC2(SC_):
    """Spectral. The continuum scale (continuum flux at the reference wavelength). The unit is decided by the user."""
    help_str = 'Star 2. Spectral continuum scale'

class SL_(FloatParameter):
    fmt_lcin = F.f9_2
    unit = 1.0 / u.micron

class SL1(SL_):
    """Spectral. The continuum slope in flux units per micron."""
    help_str = 'Star 1. Spectral continuum slope'

class SL2(SL_):
    """Spectral. The continuum slope in flux units per micron."""
    help_str = 'Star 2. Spectral continuum slope'

class NF_(IntParameter):
    fmt_lcin = F.i3
    min = 1

class NF1(NF_):
    """Spectral. Grid fineness for micro-integration on each surface element.
    NF1=1 means that there is no micro-integration. NF1=n breaks each surface element into n^2 pieces,
    each with its own radial velocity, thus improving integration accuracy."""
    help_str = 'Star 1. Spectral, grid fineness'

class NF2(NF_):
    """Spectral. Grid fineness for micro-integration on each surface element.
    NF2=1 means that there is no micro-integration. NF2=n breaks each surface element into n^2 pieces,
    each with its own radial velocity, thus improving integration accuracy."""
    help_str = 'Star 2. Spectral, grid fineness'


class WLL(FloatParameter):
    """The line rest wavelength in microns for a line of star 1 or 2"""
    help_str = 'line rest wavelength'
    fmt_lcin = F.f9_6
    nan_value = -1.
    unit = u.micron

    def isnan(self):
        return self.val < 0.0


class EWID(FloatParameter):
    """The line equivalent width, in microns – the traditional measure of line strength, for a line of star 1 (or 2).
    Absorption and emission lines both have positive equivalent width by program convention.
    Whether a line is in absorption or emission is controlled by parameters DEPTH"""
    help_str = 'line equivalent width'
    fmt_lcin = F.d12_5
    min = 0.0


class DEPTH(FloatParameter):
    """Rectangular line depth for a line of star 1 (or 2). Line profiles are formed by binning of Doppler shifted
    elements that have rectangular profiles, each with a depth and a width.
    The user supplies the depth and the program then calculates the width needed to reproduce the specified equivalent
    width. The depth is relative to a unit continuum, so 0.80000 means that 80 percent of the continuum flux
    is missing within the rectangular profile element, or that the residual flux is 20 percent of the continuum.
    Negative depths correspond to emission lines, so −0.50000 means 50 percent above the continuum.
    Depths must be less than 1.0000 (i.e. an absorption line cannot go to zero flux or below),
    but can be less than −1.0000 (an emission line can go arbitrarily high)."""
    help_str = 'line rectangular depth'
    fmt_lcin = F.f10_5
    max = 1.0

class KKS(IntParameter):
    """This integer specifies a surface region associated with a given spectral line.
    If KKS=0, the line is not specific to a location but applies to the entire star.
    If KKS=1, then the line applies only to the first spot on that star;
    if KKS=2 it applies only to the second spot, and so on.
    Naturally the star must have spots for this scheme to work, but the spots need not be hot or cool spots
    – they can have temperature factors of unity.
    Negative KKS specifies avoidance of regions. Thus KKS=−4 means that the spectral line applies everywhere on
    the star except within spot 4.
    If you find this confusing, just set KKS=0 and the line applies in the old simple way – everywhere on the star."""
    fmt_lcin = F.i5
    help_str = 'line region'

class XLAT(FloatParameter):
    """ The “latitude” of a star spot center, measured from 0 radians at the “north” (+z) pole
    to π radians at the “south” pole."""
    help_str = 'spot latitude'
    fmt_lcin = F.f9_5
    unit = u.rad
    nan_value = 300.0

    def isnan(self):
        return self.val >= 200.0


class XLONG(FloatParameter):
    """ The longitude of a star spot center, measured counter-clockwise (as viewed from above the +z axis)
    from the line of star centers from 0 to 2π radians. """
    help_str = 'spot longitude'
    fmt_lcin = F.f9_5
    unit = u.rad


class RADSP(FloatParameter):
    """The angular radius of a star spot, in radians.
    The angle is subtended by the spot radius at the center of the star. """
    help_str = 'spot radius'
    fmt_lcin = F.f9_5
    unit = u.rad


class TEMSP(FloatParameter):
    """The “temperature factor” of a spot that specifies the ratio of local spot temperature to local temperature
    that would obtain without the spot.
    A TEMSP larger or smaller than unity corresponds to the spot being hotter or cooler than the un-spotted surface, respectively.
    TEMSP is constant for a given spot, but local temperature will vary over a spot if the underlying un-spotted
    temperature varies."""
    help_str = 'spot temperature factor'
    fmt_lcin = F.f9_5
    min = 0.0


class XCL(FloatParameter):
    """Rectangular coordinate x of the centers of spherical circumstellar cloud.
    The x coordinate is zero at the center of star 1 and increases toward star 2, reaching +D at the center of star 2.
    The x, y, z system is right handed and serves for the entire binary system."""
    fmt_lcin = F.f9_4
    help_str = 'cloud x'
    nan_value = 150.0

    def isnan(self):
        return self.val >= 100.0


class YCL(FloatParameter):
    """Rectangular coordinate y of the centers of spherical circumstellar cloud"""
    fmt_lcin = F.f9_4
    help_str = 'cloud y'


class ZCL(FloatParameter):
    """Rectangular coordinate z of the centers of spherical circumstellar cloud"""
    fmt_lcin = F.f9_4
    help_str = 'cloud z'


class RCL(FloatParameter):
    """Radii of individual circumstellar spherical attenuating regions in unit of a"""
    fmt_lcin = F.f7_4
    help_str = 'cloud radii'


class OP1(FloatParameter):
    fmt_lcin = F.d11_4

class FCL(FloatParameter):
    help_str = 'f band opacity fraction'
    fmt_lcin = F.f9_4

class EDENS(FloatParameter):
    """(ne): Electron densities in cm^−3 for individual attenuating cloud.
    For a given cloud, ne is constant, although clouds can be nested or overlapped."""
    help_str = 'ne cloud electron density'
    fmt_lcin = F.d11_3

class XMUE(FloatParameter):
    """(μe): Mean molecular weight in atomic mass units per free electron for individual attenuating cloud,
    and constant throughout a given cloud."""
    help_str = 'μe cloud mean molecular weight'
    fmt_lcin = F.f9_4

class ENCL(FloatParameter):
    """(α): Exponent in the wavelength-dependent term of the attenuation law for individual attenuating cloud.
    The program internally computes densities, ρ, from ne and μe."""
    help_str = 'α cloud attenuation law exponent'
    fmt_lcin = F.f7_3




