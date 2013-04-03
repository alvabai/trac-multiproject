"""
Provides custom logger for multiproject aware trac
Requires Trac patch `logging.patch`
"""

import logging
from logging.handlers import WatchedFileHandler
import os

# registry for logger instances
_loggers = {}


class UmaskWatchedFileHandler(WatchedFileHandler):

    """
    Same as WatchedFileHandler but provides file creation with certain umask.

    Constructor default (0112) provides group write permissions
    """

    def __init__(self, filename, umask=0112):
        if not isinstance(filename, basestring):
            raise ValueError('filename must be a string, got %r' % filename)
        self.umask = umask
        old_umask = os.umask(self.umask)
        try:
            # This does not work on py 2.6
            # WatchedFileHandler is probably old style class in 2.6
            # super(UmaskWatchedFileHandler, self).__init__(filename)
            WatchedFileHandler.__init__(self, filename)
        finally:
            os.umask(old_umask)

    def emit(self, record):
        old_umask = os.umask(self.umask)
        try:
            # This does not work on py 2.6
            # WatchedFileHandler is probably old style class in 2.6
            # super(UmaskWatchedFileHandler, self).emit(record)
            WatchedFileHandler.emit(self, record)
        finally:
            os.umask(old_umask)


def logger_factory(logfile=None, level='WARNING', logid='Trac', format=None, **kwargs):
    """
    Factory for offering a logger instance for both Trac and multiproject. This is
    overriding Trac's internal (due to multiproject patch), and is called for
    all log initializations.

    Due to Trac's environment log initialization, we will need to use the log file
    as an identifier instead of the given in log id. This is because trac environments
    init their own logs with specific id, causing multiproject environment potentially
    hit file descriptor limit.

    :param str logfile: The logfile path
    :param str level: The log level
    :param str logid: Given in log id, unused
    :param str format: Optional log format
    :param kwargs: Unused, for future expansion?
    :returns: Tuple of logger and handler
    """
    # Check if there is already logger for this identifier
    # if we do this many times the lines in log file are going to duplicate.
    # The reason this is called many times is because each trac.env.Environment
    # instantiation starts logging.
    if logfile in _loggers:
        logger, hdlr = _loggers[logfile]

        # We will create a new logger instance if we have no handlers. This check
        # is here only because Trac closes environments, which in turn close
        # log handlers, so in theory we might be returning a logger without a
        # handler.
        if logger.handlers:
            logger.debug('returning previously created logger %s' % logfile)
            return logger, hdlr

    logger = logging.getLogger(logfile)
    hdlr = UmaskWatchedFileHandler(logfile)

    if not format:
        format = '%(asctime)s Trac[%(module)s] %(levelname)s: %(message)s'

    level = level.upper()
    if level in ('DEBUG', 'ALL'):
        logger.setLevel(logging.DEBUG)
    elif level == 'INFO':
        logger.setLevel(logging.INFO)
    elif level == 'ERROR':
        logger.setLevel(logging.ERROR)
    elif level == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.WARNING)

    formatter = logging.Formatter(format)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)

    # store to instance registry
    _loggers[logfile] = (logger, hdlr)
    logger.debug('new logger instance logfile: "%s"' % logfile)

    return logger, hdlr
