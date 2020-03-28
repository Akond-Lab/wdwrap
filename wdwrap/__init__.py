

# Following imports allows `from wdwrap import u` to match phoebe2 convention
import astropy.constants as c
import astropy.units as u

# Convenience functions

def default_binary(default_file=None, bundleno=0):
    from .bundle import Bundle
    """
    Returns default binary system bundle (set of parameters for LC program)
    Parameters
    ----------
    default_file : str
        name of template, see `default_wd_files`
    bundleno : int
        which set of parameters form template file has to be loaded in the case of multiple
    Returns
    -------
        Bundle
    """
    return Bundle.default_binary(default_file=default_file, bundleno=bundleno)
