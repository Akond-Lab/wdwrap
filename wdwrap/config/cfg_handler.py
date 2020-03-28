
""" cfg_handler.py: This module reads the configuration file and make the configuration params
                    for use for other modules """

import os
try:
    from configparser import ConfigParser  # python 3
except ImportError:
    from ConfigParser import ConfigParser  # python 2


class CfgHandlerError(Exception):
    pass


class CfgHandler(ConfigParser, object):
    """
    CfgHandler handles all configuration related task; Reads
    the configuration file and make all configuration parameters
    available for use.
    """

    _defaultConfigFileName = "wdwrap.ini"
    _configFileInUse = None
    _defaultInstance = None

    def __init__(self, cfg_file=None):
        """
        Constructor
        @param cfg_file: Configuration file path with name,
         if not provided then default is used: config/wdwrap.ini
        """
        super(CfgHandler, self).__init__()
        self.load_configuration(cfg_file)

    def load_configuration(self, cfg_file):
        """
        Load the configuration file in memory
        @raise CfgHandlerError: If configuration file cannot be loaded
        """
        if cfg_file is None:
            cfg_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), self._defaultConfigFileName)

        self._configFileInUse = cfg_file
        lst = self.read(self._configFileInUse)

        if len(lst) == 0:
            raise CfgHandlerError("Config file not found")

    def get_cfg_file_in_use(self):
        return self._configFileInUse

    @classmethod
    def default_instance(cls):
        if cls._defaultInstance is None:
            cls._defaultInstance = CfgHandler()
        return cls._defaultInstance

    @classmethod
    def set_config_file(cls, cfg_file):
        cls._defaultInstance = CfgHandler(cfg_file)
