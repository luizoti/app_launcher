import logging
from functools import lru_cache
from pathlib import Path

from PySide6.QtGui import QColor, QIcon, QPixmap

from src.gui.icons.rc_icons import qInitResources
from src.settings import Settings, get_config_directory, get_settings
from src.types.schemas import MAX_ICON_NAME_LENGTH

qInitResources()

logger: logging.Logger = logging.getLogger(__name__)
settings: Settings = get_settings()


def _get_icons_dir() -> Path:
    return get_config_directory() / "icons"


def _generate_missing_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(100, 100, 100))
    return QIcon(pixmap)


@lru_cache(maxsize=128)
def _load_icon_from_path(path: str) -> QIcon:
    return QIcon(path)


@lru_cache(maxsize=64)
def _load_icon_from_resource(resource_path: str) -> QIcon:
    return QIcon(QPixmap(resource_path))


def _is_valid_icon_name(icon: str) -> bool:
    """Evita OSError no filesystem com valores corrompidos no settings.

    Ex.: strings base64 legadas (>255 caracteres) salvas em menu.hide/menu.settings.
    """
    if len(icon) > MAX_ICON_NAME_LENGTH:
        return False
    if icon.strip() != icon or "\n" in icon or "\r" in icon:
        return False
    return True


def get_icon(icon: str | None = None) -> QIcon:
    icons_dir = _get_icons_dir()

    if not icon:
        resource_path = ":/icons/missing.ico"
        try:
            return _load_icon_from_resource(resource_path)
        except Exception:
            return _generate_missing_icon()

    if not _is_valid_icon_name(icon):
        logger.warning(
            f"Invalid icon name in settings ({len(icon)} chars, "
            f"first 40: {icon[:40]!r}); using fallback icon"
        )
        return _generate_missing_icon()

    possible_path = Path(icon)
    if possible_path.is_absolute() and possible_path.exists():
        return _load_icon_from_path(str(possible_path.resolve()))

    local_path = icons_dir / icon
    if local_path.exists():
        return _load_icon_from_path(str(local_path.resolve()))

    resource_path = f":/icons/{icon}"
    try:
        return _load_icon_from_resource(resource_path)
    except Exception:
        logger.warning(f"Icon not found: {icon}")
        return _generate_missing_icon()
