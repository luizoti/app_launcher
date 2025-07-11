import sys

import json
import os

CONFIG_FILE_NAME = "settings.json"
ALLOWED_DEVICES = []
DEVICES_MAPPING = {}

# determine if application is a script file or frozen exe
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
elif __file__:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# if not ALLOWED_DEVICES:
#     ALLOWED_DEVICES = [x for x in load_config().keys()]


class SettingsManager:
    _instance = None
    _config_data = {}

    def get_settings(self):
        return self._config_data.get("settings")

    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance

    def _load_config(self, path):
        if not path:
            possible_config_files = [
                os.path.join(os.path.expanduser("~"), ".config", CONFIG_FILE_NAME),
                os.path.join(BASE_DIR, CONFIG_FILE_NAME),
            ]
        else:
            possible_config_files = [path]
        print("INFO - Looking for config file in:", possible_config_files)
        for file in possible_config_files:
            if os.path.exists(file):
                with open(file, 'r', encoding='utf-8') as config_file:
                    self._config_data = json.load(config_file)
                    config_file.close()

    def get(self, key, default=None):
        return self._config_data.get(key, default)

    def set(self, key, value):
        self._config_data[key] = value

    def save(self, path="config.json"):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._config_data, f, indent=4)
