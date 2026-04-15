import logging
from functools import lru_cache
from pathlib import Path

from PySide6.QtGui import QColor, QIcon, QPixmap

from src.gui.icons.rc_icons import qInitResources
from src.settings import CONFIG_DIRECTORY, Settings, get_settings

qInitResources()

logger: logging.Logger = logging.getLogger(__name__)
settings: Settings = get_settings()


def _get_icons_dir() -> Path:
    return CONFIG_DIRECTORY / "icons"


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


def get_icon(icon: str | None = None) -> QIcon:
    icons_dir = _get_icons_dir()

    if not icon:
        resource_path = ":/icons/missing.ico"
        try:
            return _load_icon_from_resource(resource_path)
        except Exception:
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
