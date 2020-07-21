#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab


def logger(name_it=None):
    try:
        return logger.loggers[__name__]
    except AttributeError:
        logger.loggers = {}
    except LookupError:
        pass
    import logging
    if name_it is None:
        name_it = __name__
    log = logging.getLogger(name_it)
    logger.loggers[__name__] = log
    return log

# def init_logger(name, **kwargs):
#     import logging
#     log = logging.getLogger(name)
#     logger.loggers[__name__] = log
#     return log

