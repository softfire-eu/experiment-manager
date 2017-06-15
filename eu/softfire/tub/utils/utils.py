import configparser
import json
import logging
import logging.config
import os
import sys
from threading import Thread, Event

from eu.softfire.tub.utils.static_config import CONFIG_FILE_PATH


def get_logger(name):
    logging.config.fileConfig(CONFIG_FILE_PATH)
    return logging.getLogger(name)


def get_config_parser():
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


def get_config(section, key, default=None):
    config = get_config_parser()
    if default is None:
        return config.get(section=section, option=key)
    try:
        return config.get(section=section, option=key)
    except configparser.NoOptionError:
        return default
    except configparser.NoSectionError:
        return default


def get_mapping_managers():
    """{
    'sdn-manager': [
        'SdnResource'
    ],
    'nfv-manager': [
        'NfvResource'
    ],
    'monitoring-manager': [
        'MonitoringResource'
    ],
    'security-manager': [
        'SecurityResource'
    ],
    'physical-device-manager': [
        'PhysicalResource'
    ]
}"""

    with open(get_config('system', 'mapping-manager-file', '/etc/softfire/mapping-managers.json')) as f:
        return json.loads(f.read())


class ExceptionHandlerThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        if sys.version_info > (3, 0):
            super().__init__(group, target, name, args, kwargs, daemon=daemon)
        else:
            super(self.__class__, self).__init__(group, target, name, args, kwargs, daemon=daemon)
        self.exception = None

    def run(self):
        try:
            if sys.version_info > (3, 0):
                super().run()
            else:
                super(self.__class__, self).run()
        except Exception as e:
            self.exception = e


class TimerTerminationThread(Thread):
    def __init__(self, days: int, func, *args):
        super().__init__()
        self.event = Event()
        self.days = days
        self.function = func
        self.args = args

    def run(self):
        # while not self.event.wait(self.days):
        while not self.event.wait(86400 * self.days):
            self.function(*self.args[0])
            if not self.event.is_set():
                self.event.set()

    def stop(self):
        self.event.set()
