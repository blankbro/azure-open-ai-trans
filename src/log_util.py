import logging
import os.path
from logging.handlers import RotatingFileHandler

log_dir = 'logs'
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


def getLogger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(root_handler)
    logger.addHandler(error_handler)
    return logger
