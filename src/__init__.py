import os
import sys

CONFIG_FILE_NAME = ".autostart.py"
ALLOWED_DEVICES = []
DEVICES_MAPPING = {}

# determine if application is a script file or frozen exe
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
elif __file__:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def load_config():
    possible_config_files = [
        os.path.join(os.path.expanduser("~"), ".config", CONFIG_FILE_NAME),
        os.path.join(BASE_DIR, CONFIG_FILE_NAME),
    ]
    print("INFO - Looking for config file in:", possible_config_files)
    for file in possible_config_files:
        if os.path.exists(file):
            with open(file, "r") as config_file:
                exec(config_file.read(), globals())
                config_file.close()
                return DEVICES_MAPPING
    print("INFO - Config file not found. Exiting.")
    sys.exit(0)


if not ALLOWED_DEVICES:
    ALLOWED_DEVICES = [x for x in load_config().keys()]
