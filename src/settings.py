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
    DEFAULT_BLOCK_IF_RUNNING,
    DEFAULT_MAPPINGS,
    DEFAULT_MENU,
    DEFAULT_TRAY,
    DEFAULT_WINDOW,
)
from src.types.schemas import (
    AppsModel,
    DeviceMappingsModel,
    IconsModel,
    MenuModel,
    WindowModel,
)

CONFIG_FILE_NAME = "settings.json"

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
            logger.debug("Config directory founded:", path)
            return path
    joined_paths = ", ".join(map(str, possible_config_files))
    logger.debug(f"No config directory founded in possible locations: {joined_paths}")
    return Path(BASE_DIR)


@lru_cache(maxsize=1)
def get_config_directory() -> Path:
    return _select_config_directory()


def _get_config_file() -> None | Path:
    config_file = get_config_directory().joinpath(CONFIG_FILE_NAME)
    if config_file.exists() and config_file.is_file():
        return config_file.resolve()
    return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=str(_get_config_file()),
        extra="allow",
    )

    @classmethod
    def _load_json(cls) -> dict[str, Any]:
        path = _get_config_file()
        if path and path.exists():
            with open(path) as f:
                return json.load(f)
        return {}

    @classmethod
    def _merge_apps(cls, json_apps: Any) -> dict[str, AppsModel]:
        if not json_apps:
            return DEFAULT_APPS
        defaults = {k.lower(): v for k, v in DEFAULT_APPS.items()}
        overrides = {k.lower(): v for k, v in json_apps.items()}
        return {**defaults, **overrides}

    @classmethod
    def _merge_mappings(cls, json_mappings: Any) -> dict[str, DeviceMappingsModel]:
        if not json_mappings:
            return DEFAULT_MAPPINGS
        merged = dict(DEFAULT_MAPPINGS)
        merged.update(json_mappings)
        return merged

    @classmethod
    def from_json(cls) -> "Settings":
        """Load from JSON, merge with defaults."""
        json_data = cls._load_json()

        merged = {
            "apps": cls._merge_apps(json_data.get("apps")),
            "mappings": cls._merge_mappings(json_data.get("mappings")),
            "menu": json_data.get("menu", DEFAULT_MENU.model_dump()),
            "tray": json_data.get("tray", DEFAULT_TRAY.model_dump()),
            "window": json_data.get("window", DEFAULT_WINDOW.model_dump()),
            "block_if_running": json_data.get(
                "block_if_running", DEFAULT_BLOCK_IF_RUNNING
            ),
        }

        return cls(**merged)

    apps: dict[str, AppsModel] = Field(default=DEFAULT_APPS)
    mappings: dict[str, DeviceMappingsModel] = Field(default=DEFAULT_MAPPINGS)
    menu: MenuModel = Field(default=DEFAULT_MENU)
    tray: IconsModel = Field(default=DEFAULT_TRAY)
    window: WindowModel = Field(default=DEFAULT_WINDOW)
    block_if_running: list[str] = Field(default=DEFAULT_BLOCK_IF_RUNNING)
    icons_directory: pathlib.Path | str | None = Field(default=None)

    @field_validator("icons_directory", mode="before")
    @classmethod
    def validate_icons_directory(cls, value: pathlib.Path | str | None) -> pathlib.Path:
        config_file = cls.model_config.get("env_prefix")
        if not config_file:
            raise ValueError("Config file path must be provided in env_prefix")
        config_path: pathlib.Path = pathlib.Path(config_file).parent
        logger.debug(f"Config path: {config_path}")
        return config_path.joinpath("icons")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_json()
