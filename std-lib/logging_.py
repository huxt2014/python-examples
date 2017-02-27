

import logging.config


################################################################################
#                                configure
################################################################################
# basic configuration #########################################
#     Creating a StreamHandler with a default Formatter and
# adding it to the root logger. This function does nothing if
# the root logger already has handlers configured for it.
#     This function is not thread safe, so invoke it from the
# main thread before other threads are started.
logging.basicConfig()


# dictionary-based configuration ##############################
logger_config = {
    'version': 1,
    'formatters': {
        'basic': {
            'format': '%(asctime)s-%(name)s-%(lineno)d-%(levelname)s:%(message)s'
            },
        'other_format': {
            'format': ''
            }
        },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'basic',
            'filename': 'log.txt',
            'when': 'D',
            },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
            'level': 'INFO'
            }
        },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
        },
    'loggers': {
        # suppress the log info from requests to warn level
        'requests': {
            'level': 'WARN',
            'handlers': ['file'],
            'propagate': False
            },

        },
    # if True, the logger initialized before dictConfig() will be disabled,
    # unless they (or an ancestor) are explicitly named in the configuration.
    'disable_existing_loggers': False
    }
logging.config.dictConfig(logger_config)

################################################################################
#                                 basic usage
################################################################################
# get logger ####################################################
#     Loggers are never instantiated directly, but always through
# the module-level function logging.getLogger(name). Logger
# instances are named singleton.
logger = logging.getLogger(__name__)

# module level log ##############################################
#     The module level function log a message on the root logger.
# basicConfig() will be called if no handler is available.
logging.info('msg')

################################################################################
#                                 concurrence
#     The logging module is intended to be thread-safe without any special work
# needing to be done by its clients. It achieves this though using threading
# locks; there is one lock to serialize access to the module's shared data, and
# each handler also creates a lock to serialize access to its underlying I/O.
#     If you are implementing asynchronous signal handlers using the signal
# module, you may not be able to use logging from within such handlers. This is
# because lock implementations in the threading module are not always
# re-entrant, and so cannot be invoked from such signal handlers.
#     Multiple processes is not supported, because there is no standard way to
# serialize access to a single file across multiple processes in Python. One way
# to support multiple processes is to have all the processes log to a
# SocketHandler, and have a separate process which implements a socket server
# which reads from the socket and logs to file. Or write your own handler using
# the Lock class from multiprocessing module to serialize access to the file.
################################################################################
