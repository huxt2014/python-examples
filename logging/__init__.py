
"""
    Multiple threads log to a single file is supported by default, but multiple
processes is not supported, because there is no standard way to serialize access
to a single file across multiple processes in Python.
    One way to support multiple processes is to have all the processes log to a 
SocketHandler, and have a separate process which implements a socket server 
which reads from the socket and logs to file. Or write your own handler using
the Lock class from multiprocessing module to serialize access to the file.
"""

# get a logger Instance ########################################
#     Loggers are never instantiated directly, but always through the 
# module-level function logging.getLogger(name). Multiple calls to getLogger() 
# with the same name will always return a reference to the same Logger object.
logger = logging.getLogger(__name__)



# configure #####################################################

## basic configuration
##     Creating a StreamHandler with a default Formatter and adding it to the 
## root logger. This function does nothing if the root logger already has 
## handlers configured for it.
logging.basicConfig()

## dictionary-based configuration
logger_config = {
    'version': 1,
    'formatters':{
        'basic': {
            'format': '%(asctime)s-%(name)s-%(lineno)d-%(levelname)s:%(message)s'
            },
        'other_format':{
            'format': ''
            }
        },
    'handlers':{
        'file':{
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'basic',
            'filename': os.path.join(log_dir, 'log.txt'),
            'when': 'D',
            },
        'console':{
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
            'level': 'INFO'
            }  
        },
    'root':{
        'level': 'INFO',
        'handlers': ['file', 'console']  
        },
    'loggers':{
        # suppress the log info from requests to warn level
        'requests':{
            'level': 'WARN',
            'handlers': ['file'],
            'propagate': False
            },

        },
    # if True, the logger initialized before dictConfig() will be disabled.
    'disable_existing_loggers':False
    }
logging.config.dictConfig(logger_config)


## file rotation
##     limit the file number and the size of each file
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=20, backupCount=5)



# use ######################################################

## basic log
logger.info(msg)

## module level log
##     The module level function will call basicConfig() to ensure that at least
## one handler is available, which is not thread safe.
logging.info(msg)      # log a message on the root logger.


## add contextual information
adapter = logging.LoggerAdapter(logger, {'connid': conn_id})




