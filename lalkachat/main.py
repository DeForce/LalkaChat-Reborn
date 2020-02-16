import collections
import logging.handlers
import os
from os import path

from dotmap import DotMap
import yaml

from __init__ import LOG_FOLDER, CONFIG_FOLDER
from base import Config
from server import Server


if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
LOG_FILE = os.path.join(LOG_FOLDER, 'main.log')
LOG_FORMAT = logging.Formatter("%(asctime)s [%(threadName)s %(name)s] [%(levelname)s]  %(message)s")


root_logger = logging.getLogger()
file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1000*1024, backupCount=5)
file_handler.setFormatter(LOG_FORMAT)
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(LOG_FORMAT)
root_logger.addHandler(console_handler)
logging.getLogger('requests').setLevel(logging.ERROR)


DEFAULT_PROFILE_NAME = 'default'
BASE_CONFIG_FILE = path.join(CONFIG_FOLDER, 'base.yaml')


class BaseConfig(Config):
    def __init__(self, b_config):
        self.log_level = b_config.get('log_level', logging.getLevelName(logging.INFO))
        self.profile = b_config.get('profile', DEFAULT_PROFILE_NAME)
        self.host = b_config.get('host', '0.0.0.0')
        self.port = b_config.get('port', 8082)

    def save(self):
        return {
            'log_level': self.log_level,
            'profile': self.profile,
            'host': self.host,
            'port': self.port
        }


def load_profiles():
    for dirpath, dirnames, filenames in os.walk(CONFIG_FOLDER):
        for file in filenames:
            basename = path.splitext(file)[0]
            if basename == 'base':
                continue
            with open(os.path.join(dirpath, file)) as f:
                profile_data = yaml.safe_load(f.read())
            if profile_data and isinstance(profile_data, dict):
                yield {basename: profile_data}


if __name__ == '__main__':
    # Loading configuration
    yaml_data = {}
    if not os.path.isdir(CONFIG_FOLDER):
        os.mkdir(CONFIG_FOLDER)
    elif os.path.exists(CONFIG_FOLDER):
        if path.exists(BASE_CONFIG_FILE):
            with open(BASE_CONFIG_FILE, 'r') as base_file:
                loaded = yaml.safe_load(base_file.read())
                if loaded:
                    yaml_data.update(loaded)

    base_config = BaseConfig(yaml_data)

    root_logger.setLevel(base_config.log_level)
    profiles = collections.ChainMap(*load_profiles())
    active_profile = base_config.profile

    if active_profile not in profiles:
        profiles[active_profile] = DotMap()

    server = Server(profiles, active_profile, base_config)
    server.run_server()
    profiles[base_config.profile] = server.save()

    for profile, config in profiles.items():
        with open(os.path.join(CONFIG_FOLDER, f'{profile}.yaml'), 'w') as p_config:
            p_config.write(yaml.safe_dump(config))
    with open(BASE_CONFIG_FILE, 'w') as b_file:
        b_file.write(yaml.safe_dump(base_config.save()))
    logging.info('Wrote configuration successfully, exiting')
