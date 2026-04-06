import base64
import logging
from functools import lru_cache
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap

from src.settings import Settings, get_settings

logger: logging.Logger = logging.getLogger(__name__)
settings: Settings = get_settings()


def _get_icons_dir() -> Path:
    if not settings.icons_directory:
        raise ValueError("Icons directory is not set in settings")
    return Path(settings.icons_directory).resolve()


@lru_cache(maxsize=128)
def _load_icon_from_path(path: str) -> QIcon:
    """
    Cached loader for file-based icons.
    Path must already be absolute/resolved.
    """
    return QIcon(path)


@lru_cache(maxsize=64)
def _load_icon_from_base64(data: str) -> QIcon:
    """
    Cached loader for base64 icons.
    """
    pixmap = QPixmap()
    pixmap.loadFromData(base64.b64decode(data))
    return QIcon(pixmap)


def get_icon(icon: str | None = None) -> QIcon:
    """
    Load icon from:
    - None -> missing.ico
    - filename inside icons directory
    - absolute path
    - base64 string
    """

    icons_dir = _get_icons_dir()

    if not icon:
        missing_path = (icons_dir / "missing.ico").resolve()
        if not missing_path.exists():
            raise FileNotFoundError(f"Missing icon not found: {missing_path}")
        return _load_icon_from_path(str(missing_path))

    possible_path = Path(icon)
    if possible_path.is_absolute() and possible_path.exists():
        return _load_icon_from_path(str(possible_path.resolve()))

    try:
        local_path = (icons_dir / icon).resolve()
        if local_path.exists():
            return _load_icon_from_path(str(local_path))
    except OSError:
        pass

    try:
        return _load_icon_from_base64(icon)
    except Exception as e:
        logger.exception("Failed to load icon from base64")
        raise ValueError("Invalid icon input") from e
