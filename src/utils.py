import base64
import typing
from pathlib import Path

import psutil
from PySide6.QtGui import QIcon, QImage, QPixmap

from src.settings import SettingsManager, SettingsModel


def build_icon(
    icon: typing.Optional[typing.Text] = None, settings: SettingsModel=SettingsManager().get_settings()
) -> QIcon:
    """
    Load ico from file or base64 and return a QIcon, loads absolute path, filename from icos directory or base64 string.
    
    :param icon: base64 or icon name or absolute ico path
    :type icon: typing.Optional[typing.Text]
    :param settings: App Settings model
    :type settings: SettingsModel
    :return: QIcon based on loaded icon file
    :rtype: QIcon
    """
    local_icon_directory: Path = Path(settings.icons_directory)
    if not icon:
        return QIcon(str(local_icon_directory.joinpath("missing.ico")))
    try:
        if local_icon_directory.joinpath(icon).exists():
            return QIcon(str(local_icon_directory.joinpath(icon)))
    except (OSError, TypeError):
        pass
    image = QImage()
    image.loadFromData(base64.b64decode(icon))
    return QIcon(QPixmap.fromImage(image))


def check_running_processes(search_process: typing.Text):
    if not search_process:
        raise ValueError("Argument `search_process` cannot be None")

    return (
        x
        for x in [x.info["name"].lower() for x in psutil.process_iter(["name"])]
        if x in [process.lower() for process in search_process]
    )
