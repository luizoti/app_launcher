import typing
from typing import Dict, List, Text, Union

from pydantic import BaseModel


class AppsModel(BaseModel):
    cmd: Union[List[Text], typing.Text]
    enabled: bool
    icon: Text

class MappingsModel(BaseModel):
    buttons: Dict[Text, int]
    tray: bool

class IconsModel(BaseModel):
    connected: Text
    disconnected: Text
    standby: Text


class WindowModel(BaseModel):
    apps_per_row: int
    button_size: int
    fullscreen: bool
    height: int
    width: int


class MenuModel(BaseModel):
    hide: Text
    settings: Text


class SettingsModel(BaseModel):
    apps: Dict[Text, AppsModel]
    mappings: Dict[Text, MappingsModel]
    menu: MenuModel
    tray: IconsModel
    window: WindowModel
    icons_directory: Text
