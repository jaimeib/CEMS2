"""Logging module for CEMS2."""

import logging

from cems2 import config_loader

# Get the configuration
CONFIG = config_loader.get_config()


class CustomFormatter(logging.Formatter):
    """Custom formatter for logging.

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
        """Initialize the CustomFormatter class.

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
        """Format logs.

        :param record: Record of logs
        :type record: str

        :return: Formatted logs
        :rtype: str
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%d-%m-%Y %H:%M:%S")
        return formatter.format(record)


def _get_level(level):
    """Get the loggin level from the config file.

    :param level: Log level
    :type level: str

    :return: Log level
    :rtype: int
    """
    if level == "DEBUG":
        return logging.DEBUG
    elif level == "INFO":
        return logging.INFO
    elif level == "WARNING":
        return logging.WARNING
    elif level == "ERROR":
        return logging.ERROR
    elif level == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.INFO


def get_logger(name):
    """Get logger.

    :param name: Name of logger.
    :type name: str

    :return: Logger
    :rtype: logging
    """
    logger = logging.getLogger(name)

    # Get the log level from the config file
    try:
        level = CONFIG.get("log", "level")
    except Exception:
        level = "INFO"  # Default log level

    # Set the log level
    logger.setLevel(_get_level(level))

    # Define format for logs
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    # Get the handlers defined in the config file
    handlers = CONFIG.get("log", "handlers")

    # Create a handler for logging to stdout if is defined
    if "console" in handlers:
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(_get_level(level))
        stdout_handler.setFormatter(CustomFormatter(fmt))
        logger.addHandler(stdout_handler)

    # Create a handler for logging to a file if is defined
    if "file" in handlers and CONFIG.get("log", "file") != "":
        # Get the path of the log file
        log_file = CONFIG.get("log", "file")

        # Create file handler for logging to a file
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(_get_level(level))
        file_handler.setFormatter(logging.Formatter(fmt, datefmt="%d-%m-%Y %H:%M:%S"))
        logger.addHandler(file_handler)

    return logger
