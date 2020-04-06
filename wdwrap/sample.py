#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import pandas as pd

def sample_lc_filepath(band='V', obs ='Ibanoglu', target='LL-Aqr'):
    from .io import IO
    band = '' if band is None else f'.{band}'
    return IO.default_wd_file_abspath(f'{target}.{obs}{band}.dat', 'data')

def sample_rv_filepath(target='LL-Aqr'):
    from .io import IO
    return IO.default_wd_file_abspath(f'{target}.rv.dat', 'data')

def sample_light_dat_filepath():
    """Sample LC light.dat output"""
    from .io import IO
    return IO.default_wd_file_abspath(f'light.dat', 'data')

def sample_veloc_dat_filepath():
    """Sample LC veloc.dat output"""
    from .io import IO
    return IO.default_wd_file_abspath(f'veloc.dat', 'data')

def sample_lc_dataframe(band='V', obs ='Ibanoglu', target='LL-Aqr'):
    from .io import Reader_hjd_mag
    r = Reader_hjd_mag(sample_lc_filepath(band=band, obs=obs, target=target))
    return r.df

def sample_rv_dataframe(target='LL-Aqr'):
    from .io import Reader_ravespan_rv
    r = Reader_ravespan_rv(sample_rv_filepath(target=target))
    return r.df

def sample_light_dat_dataframe():
    from .io import Reader_light
    r = Reader_light(sample_light_dat_filepath())
    return r.df

def sample_veloc_dat_dataframe():
    from .io import Reader_veloc
    r = Reader_veloc(sample_veloc_dat_filepath())
    return r.df
