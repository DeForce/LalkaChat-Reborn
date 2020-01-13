import collections
import logging.handlers
import os
from os import path

from dotmap import DotMap
import yaml

from __init__ import LOG_FOLDER, CONFIG_FOLDER
from server import Server


if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
LOG_FILE = os.path.join(LOG_FOLDER, 'main.log')
LOG_FORMAT = logging.Formatter("%(asctime)s [%(threadName) s%(name)s] [%(levelname)s]  %(message)s")


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

base_config = DotMap({
    'log_level': logging.getLevelName(logging.INFO),
    'profile': DEFAULT_PROFILE_NAME,
    'host': '0.0.0.0',
    'port': '8081'
})


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
    if not os.path.isdir(CONFIG_FOLDER):
        raise IOError(f'Path {CONFIG_FOLDER} is not a folder')
    elif os.path.exists(CONFIG_FOLDER):
        if path.exists(BASE_CONFIG_FILE):
            with open(BASE_CONFIG_FILE, 'r') as base_file:
                yaml_data = yaml.safe_load(base_file.read())
                if yaml_data and isinstance(yaml_data, dict):
                    base_config.update(yaml_data)

    root_logger.setLevel(base_config.log_level)
    profiles = collections.ChainMap(*load_profiles())
    active_profile = base_config.profile

    server = Server(profiles, active_profile, base_config)
    server.run_server()
