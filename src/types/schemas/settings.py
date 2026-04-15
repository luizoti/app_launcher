"""Pydantic models for application settings."""

from enum import Enum

from pydantic import BaseModel


class WindowMode(str, Enum):
    """Window display modes."""

    BORDERLESS = "borderless"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"


class AppsModel(BaseModel):
    """Application entry configuration."""

    cmd: list[str] | str
    enabled: bool
    icon: str


class DeviceMappingsModel(BaseModel):
    """Device button to action mapping."""

    buttons: dict[str, str]
    tray: bool = False


class IconsModel(BaseModel):
    """System tray icon paths."""

    connected: str
    disconnected: str
    standby: str


class WindowModel(BaseModel):
    """Window configuration."""

    apps_per_row: int
    button_size: int
    fullScreen: bool
    height: int
    width: int
    window_mode: WindowMode = WindowMode.BORDERLESS


class MenuModel(BaseModel):
    """Context menu icon paths."""

    hide: str
    settings: str
