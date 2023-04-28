"""
Module for loading configuration files into the system. 
"""

import os
from configparser import ConfigParser

path_current_directory = os.path.dirname(__file__)
path_config_file = os.path.join(
    path_current_directory, "../etc/cems2/", "cems2.conf"
)  # FIXME: Path is relative


config = ConfigParser()
config.read(path_config_file)
