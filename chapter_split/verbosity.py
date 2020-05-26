"""Verbosity module."""

import logging

VERBOSE_LEVEL = 20
VVERBOSE_LEVEL = 19
VVVERBOSE_LEVEL = 18

# create logger
logger = logging.getLogger("logger")
logger.setLevel(logging.WARNING)

logging.addLevelName(VVERBOSE_LEVEL, "INFO")
logging.addLevelName(VVVERBOSE_LEVEL, "INFO")


def _vprint(self, message, *args, **kws):
    if self.isEnabledFor(VERBOSE_LEVEL):
        # Yes, logger takes its '*args' as 'args'.
        self._log(VERBOSE_LEVEL, message, args, **kws)


def _vvprint(self, message, *args, **kws):
    if self.isEnabledFor(VVERBOSE_LEVEL):
        # Yes, logger takes its '*args' as 'args'.
        self._log(VVERBOSE_LEVEL, message, args, **kws)


def _vvvprint(self, message, *args, **kws):
    if self.isEnabledFor(VVVERBOSE_LEVEL):
        # Yes, logger takes its '*args' as 'args'.
        self._log(VVVERBOSE_LEVEL, message, args, **kws)


logging.Logger.vprint = _vprint
logging.Logger.vvprint = _vvprint
logging.Logger.vvvprint = _vvvprint


# create console handler and set level to debug
ch = logging.StreamHandler()
# ch.setLevel(logging.WARNING)

# create formatter
formatter = logging.Formatter("%(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def set_level(level, debug=False):
    if debug:
        formatter = logging.Formatter("[%(levelname)s] - %(message)s")
        ch.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
    else:
        formatter = logging.Formatter("%(message)s")
        ch.setFormatter(formatter)
        logger.setLevel(level)


vprint = logger.vprint
vvprint = logger.vvprint
vvvprint = logger.vvvprint
warn = logger.warning
