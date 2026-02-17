"""
Settings module, implement a class to manage settings file.
"""

import json
import logging
import sys
import typing
from pathlib import Path
from typing import ClassVar

from src.settings_model import SettingsModel


CONFIG_FILE_NAME = "settings.json"
ALLOWED_DEVICES = []
DEVICES_MAPPING = {}

logger = logging.getLogger(__name__)


BASE_DIR: Path = Path(
    sys.executable if getattr(sys, "frozen", False) else __file__
).parent.parent


# if not ALLOWED_DEVICES:
#     ALLOWED_DEVICES = [x for x in load_config().keys()]



class SettingsManager:
    _instance: ClassVar["SettingsManager | None"] = None
    _config_data: typing.Optional[SettingsModel]

    def get_settings(self) -> SettingsModel:
        if not self._config_data:
            raise RuntimeError("Cannot load settings")
        return self._config_data

    def __new__(cls, config_path: typing.Optional[Path | None] = None):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance

    def _load_config(self, config_path: typing.Optional[Path | None]) -> None:
        if not config_path:
            possible_config_files = [
                Path("~")
                .expanduser()
                .joinpath(".config", "app_launcher", CONFIG_FILE_NAME),
                Path(BASE_DIR).joinpath(CONFIG_FILE_NAME),
            ]
        else:
            possible_config_files = [config_path]
        logger.debug("Looking for config file in:", possible_config_files)
        for file in possible_config_files:

            if not file.exists():
                continue
            icons_directory = Path(file).parent.joinpath("icons")
            icons_directory.mkdir(parents=True, exist_ok=True)

            with open(file, "r", encoding="utf-8") as config_file:
                logger.debug("Reading config file:", file)
                raw_data = json.load(config_file)

                self._config_data = SettingsModel(
                    **raw_data, icons_directory=str(icons_directory)
                )
            return

    # def _get(self, key: Text, default: Any = None) -> typing.Optional[SettingsModel]:
    #     return self._config_data.model_dump(mode="python").get(key, default)

    # def _set(
    #     self, key: Text, value: typing.Optional[Path | Text]
    # ) -> typing.Optional[bool | None]:
    #     try:
    #         self._config_data[key] = value
    #         return True
    #     except KeyError:
    #         pass
    #     return None

    def save(self, path: Path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._config_data, f, indent=4)
