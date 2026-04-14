from enum import Enum

from pydantic import BaseModel


class WindowMode(str, Enum):
    BORDERLESS = "borderless"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"


class AppsModel(BaseModel):
    cmd: list[str] | str
    enabled: bool
    icon: str


class DeviceMappingsModel(BaseModel):
    buttons: dict[str, str]
    tray: bool = False


class IconsModel(BaseModel):
    connected: str
    disconnected: str
    standby: str


class WindowModel(BaseModel):
    apps_per_row: int
    button_size: int
    fullScreen: bool
    height: int
    width: int
    window_mode: WindowMode = WindowMode.BORDERLESS


class MenuModel(BaseModel):
    hide: str
    settings: str
