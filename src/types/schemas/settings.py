"""Pydantic models for application settings."""

from enum import Enum

from pydantic import BaseModel, field_validator

#: Limite de nome de arquivo em bytes (NAME_MAX na maioria dos filesystems)
MAX_ICON_NAME_LENGTH = 255


def validate_icon_name(value: str) -> str:
    """Valida um valor de ícone do settings (esperado: nome de arquivo).

    Levanta ValueError para valores corrompidos, ex.: strings base64 legadas
    (>255 caracteres) salvas em menu.hide/menu.settings.
    """
    if len(value) > MAX_ICON_NAME_LENGTH:
        raise ValueError(
            f"icon name too long ({len(value)} chars > {MAX_ICON_NAME_LENGTH}); "
            f"expected a file name, got {value[:40]!r}... "
            "(probable un-migrated base64 value)"
        )
    if value.strip() != value:
        raise ValueError(
            f"icon name must not have leading/trailing whitespace: {value[:40]!r}"
        )
    return value


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

    @field_validator("icon")
    @classmethod
    def _check_icon(cls, value: str) -> str:
        return validate_icon_name(value)


class DeviceMappingsModel(BaseModel):
    """Device button to action mapping."""

    buttons: dict[str, str]
    tray: bool = False


class IconsModel(BaseModel):
    """System tray icon paths."""

    connected: str
    disconnected: str
    standby: str

    @field_validator("connected", "disconnected", "standby")
    @classmethod
    def _check_icon(cls, value: str) -> str:
        return validate_icon_name(value)


class WindowModel(BaseModel):
    """Window configuration."""

    apps_per_row: int
    button_size: int
    height: int
    width: int
    window_mode: WindowMode = WindowMode.BORDERLESS


class MenuModel(BaseModel):
    """Context menu icon paths."""

    hide: str
    settings: str

    @field_validator("hide", "settings")
    @classmethod
    def _check_icon(cls, value: str) -> str:
        return validate_icon_name(value)
