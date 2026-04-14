"""
Settings module, implement a class to manage settings file.
"""

import json
import logging
import pathlib
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.default_settings import (
    DEFAULT_APPS,
    DEFAULT_MAPPINGS,
    DEFAULT_MENU,
    DEFAULT_TRAY,
    DEFAULT_WINDOW,
)
from src.settings_model import (
    AppsModel,
    DeviceMappingsModel,
    IconsModel,
    MenuModel,
    WindowModel,
)

CONFIG_FILE_NAME = "settings.json"
ALLOWED_DEVICES = []
DEVICES_MAPPING = {}

logger: logging.Logger = logging.getLogger(__name__)


BASE_DIR: Path = Path(
    sys.executable if getattr(sys, "frozen", False) else __file__
).parent.parent


def _select_config_directory() -> Path:
    possible_config_files: list[Path] = [
        Path("~").expanduser().joinpath(".config", "app_launcher"),
    ]
    for path in possible_config_files:
        if path.exists():
            logger.info("Config directory founded:", path)
            return path
    joined_paths = ", ".join(map(str, possible_config_files))
    logger.info(f"No config directory founded in possible locations: {joined_paths}")
    return Path(BASE_DIR)


def _get_config_file() -> None | Path:
    config_file = CONFIG_DIRECTORY.joinpath(CONFIG_FILE_NAME)
    if config_file.exists() and config_file.is_file():
        return config_file.resolve()
    return None


CONFIG_DIRECTORY = _select_config_directory()

# if not ALLOWED_DEVICES:
#     ALLOWED_DEVICES = [x for x in load_config().keys()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=str(_get_config_file()),
        extra="allow",
    )

    @classmethod
    def from_json(cls) -> "Settings":
        """Carrega do JSON, merge com defaults."""
        json_path: Path | None = _get_config_file()

        json_data: dict[str, Any] = {}
        if json_path:
            if json_path.exists() and json_path.is_file():
                with open(json_path) as f:
                    json_data = json.load(f)

        merged_data = {}

        if "apps" in json_data:
            defaults: dict[str, AppsModel] = {
                x.lower(): y for x, y in DEFAULT_APPS.items()
            }
            json_apps: dict[str, str] = {
                x.lower(): y for x, y in json_data["apps"].items()
            }
            merged_data["apps"] = {**defaults, **json_apps}
        else:
            merged_data["apps"] = DEFAULT_APPS

        if "mappings" in json_data:
            merged_mappings: dict[str, DeviceMappingsModel] = dict(DEFAULT_MAPPINGS)
            for k, v in json_data["mappings"].items():
                if k in merged_mappings:
                    merged_mappings[k] = v
                else:
                    merged_mappings[k] = v
            merged_data["mappings"] = merged_mappings
        else:
            merged_data["mappings"] = DEFAULT_MAPPINGS

        if "menu" in json_data:
            merged_data["menu"] = json_data["menu"]
        else:
            merged_data["menu"] = DEFAULT_MENU.model_dump()

        if "tray" in json_data:
            merged_data["tray"] = json_data["tray"]
        else:
            merged_data["tray"] = DEFAULT_TRAY.model_dump()

        if "window" in json_data:
            merged_data["window"] = json_data["window"]
        else:
            merged_data["window"] = DEFAULT_WINDOW.model_dump()

        return cls(**merged_data)

    apps: dict[str, AppsModel] = Field(default=DEFAULT_APPS)
    mappings: dict[str, DeviceMappingsModel] = Field(default=DEFAULT_MAPPINGS)
    menu: MenuModel = Field(default=DEFAULT_MENU)
    tray: IconsModel = Field(default=DEFAULT_TRAY)
    window: WindowModel = Field(default=DEFAULT_WINDOW)
    icons_directory: pathlib.Path | str | None = Field(default=None)

    @field_validator("icons_directory", mode="before")
    @classmethod
    def validate_icons_directory(cls, value: pathlib.Path | str | None) -> pathlib.Path:
        config_file = cls.model_config.get("env_prefix")
        if not config_file:
            raise ValueError("Config file path must be provided in env_prefix")
        config_path: pathlib.Path = pathlib.Path(config_file).parent
        logger.info(f"Config path: {config_path}")
        return config_path.joinpath("icons")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_json()
