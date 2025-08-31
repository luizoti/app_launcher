import base64
import psutil
from PyQt5.QtGui import QIcon, QImage, QPixmap
from typing import Generator


def base64_to_icon(icon=None, connected=False) -> QIcon:
    image = QImage()
    image.loadFromData(base64.b64decode(icon))
    return QIcon(QPixmap.fromImage(image))


def check_running_processes(search_process=None) -> Generator[str]:
    if not search_process:
        raise ValueError("Argument `search_process` cannot be None")

    return (x for x in [x.info["name"].lower() for x in psutil.process_iter(["name"])] if
            x in [p.lower() for p in search_process])
