import configparser
import os

import logging
import logging.config

from eu.softfire.tub.utils.static_config import CONFIG_FILE_PATH


def get_logger(name):
    logging.config.fileConfig(CONFIG_FILE_PATH)
    return logging.getLogger(name)


def get_config():
    """
    Get the ConfigParser object containing the system configurations

    :return: ConfigParser object containing the system configurations
    """
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE_PATH) and os.path.isfile(CONFIG_FILE_PATH):
        config.read(CONFIG_FILE_PATH)
        return config
    else:
        logging.error("Config file not found, create %s" % CONFIG_FILE_PATH)
        exit(1)
