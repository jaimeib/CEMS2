"""
Logging module for CEMS2
"""

import logging


class CustomFormatter(logging.Formatter):
    """
    Custom formatter for logging

    :param logging.Formatter: Logging module
    :type logging.Formatter: logging
    """

    green = "\x1b[38;5;10m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt):
        """
        Constructor

        :param fmt: Format of logs
        :type fmt: str
        """
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.green + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        """
        Format logs

        :param record: Record of logs
        :type record: str

        :return: Formatted logs
        :rtype: str
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%d-%m-%Y %H:%M:%S")
        return formatter.format(record)


def get_logger(name):
    """
    Get logger

    :param name: Name of logger
    :type name: str

    :return: Logger
    :rtype: logging
    """
    logger = logging.getLogger(name)

    # Create custom logger logging all five levels
    logger.setLevel(logging.DEBUG)

    # Define format for logs
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    # Create stdout handler for logging to the console (logs all five levels)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(CustomFormatter(fmt))

    # Create file handler for logging to a file (logs all five levels)
    file_handler = logging.FileHandler("logs/system.log", mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt, datefmt="%d-%m-%Y %H:%M:%S"))

    # Add both handlers to the logger
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    return logger
