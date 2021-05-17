import logging.handlers
from src.config import get_settings


def setup_logging():
    # create logger with 'spam_application'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s',
                        datefmt='%m-%d %H:%M')

    # create file handler which logs even debug messages
    fh = logging.handlers.RotatingFileHandler(f'{get_settings().RUNTIME_ENV}-server.log', maxBytes=1024 * 1024*  10, backupCount=5)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the root logger
    root_logger = logging.getLogger('')
    root_logger.addHandler(fh)
    root_logger.addHandler(ch)

