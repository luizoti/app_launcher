from pydantic import BaseModel


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


class MenuModel(BaseModel):
    hide: str
    settings: str
