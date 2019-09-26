

# allow  `from wdwrap import u` to match phoebe2 convention

import astropy.constants as c
import astropy.units as u


# Convenience functions

def default_binary(default_file=None, bundleno=0):
    from .bundle import Bundle
    return Bundle.default_binary(default_file=default_file, bundleno=bundleno)
