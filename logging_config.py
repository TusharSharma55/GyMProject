import logging
from logging.handlers import RotatingFileHandler


file_handler = logging.FileHandler("AllLogs/log_details.log")
log_formatter = "%(asctime)s ** %(message)s ** %(levelname)s ** %(lineno)s"

formater = logging.Formatter(log_formatter)
