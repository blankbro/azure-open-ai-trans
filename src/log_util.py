import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

load_dotenv()

log_dir = os.getenv("LOG_DIR", default='logs')
root_log_file = f'{log_dir}/info.log'
error_log_file = f'{log_dir}/error.log'

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# root info.log
root_handler = RotatingFileHandler(root_log_file, encoding='utf-8', maxBytes=1024 * 1024)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] [%(funcName)s:%(lineno)d] - %(message)s')
root_handler.setFormatter(formatter)

# error.log
error_handler = RotatingFileHandler(error_log_file, encoding='utf-8', maxBytes=1024 * 1024)
error_handler.setFormatter(formatter)
error_filter = logging.Filter()
error_filter.filter = lambda record: record.levelno >= logging.ERROR
error_handler.addFilter(error_filter)


# Console log
class ConsoleHandler(logging.StreamHandler):
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)

    @property
    def stream(self):
        return sys.stdout


console_handler = ConsoleHandler()
console_handler.setFormatter(formatter)


def get_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    add_handler(logger)
    return logger


def add_handler(logger):
    logger.addHandler(root_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
