"""Module for loading configuration files into the system."""


import os
from configparser import ConfigParser

config_file_path = os.path.join(os.path.dirname(__file__), "config.ini")

config = ConfigParser(converters={"list": lambda x: [i.strip() for i in x.split(",")]})
config.read(config_file_path)


def get_config():
    """Get the configuration."""
    return config
