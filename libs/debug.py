import logging

LOGFILE = "G:\\Downloads\\python\\AHArbitrage\\logs\\error.log"
LOGLEVEL = logging.DEBUG
DEBUG_OUTPUT = True


def debug(e, flush=True, output=DEBUG_OUTPUT):
    """Print exception message.

    Args:
        e (Exception): Exception reported
        flush (bool, optional): Flush output
        output (bool, optional): If debugging is enabled, print message
    """
    if output:
        print(e, flush=flush)


def log(e, traceback=True):
    """Appends exception to log file.

    Args:
        e (TYPE): Description
        traceback (bool, optional): Logs full traceback (default: True)
    """
    logging.basicConfig(filename=LOGFILE,
                        level=LOGLEVEL,
                        format='%(asctime)s\t\t\n%(message)s\n',
                        datefmt='%m/%d/%Y %H:%M:%S')

    if traceback:
        logging.exception(e)
    else:
        logging.debug(e)


'''
try:
    #raise Exception('spam', 'eggs')
    print(123 + "THIS IS A TEST")
except Exception as e:
    debug(e.args)
    log(e.args)
'''
