#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

class FileFormatError(Exception):
    pass


class FileFormatNotSupportedError(FileFormatError):
    pass


class FileFormatMultipleSetsError(FileFormatError):
    pass


class FileFormatVersionError(FileFormatError):
    pass