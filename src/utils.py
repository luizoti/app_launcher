import base64
from pathlib import Path

import psutil
from PyQt5.QtGui import QIcon, QPixmap, QImage

from src.settings import SettingsManager


def build_icon(icon=None, settings=SettingsManager().get_settings()) -> QIcon | QIcon | None:
    try:
        if Path(icon).exists():
            return QIcon(icon)

        local_icon: Path = settings.get("icons_directory").joinpath(icon)

        if local_icon.exists():
            return QIcon(str(local_icon))
    except (OSError, TypeError):
        image = QImage()
        image.loadFromData(base64.b64decode(icon))
        return QIcon(QPixmap.fromImage(image))


def check_running_processes(search_process=None):
    if not search_process:
        raise ValueError("Argument `search_process` cannot be None")

    return (x for x in [x.info["name"].lower() for x in psutil.process_iter(["name"])] if
            x in [p.lower() for p in search_process])
