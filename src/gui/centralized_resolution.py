from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QApplication


class CentralizedAppResolution:
    def __init__(self, app=None):
        super(CentralizedAppResolution, self).__init__()
        self.geometry: QRect = QApplication.primaryScreen().geometry()
        self.app = app

    def centralized_resolution(self) -> QPoint | QPoint:
        width = ((self.geometry.width() - self.app.width()) // 2)
        height = ((self.geometry.height() - self.app.height()) // 2)
        return QPoint(width, height)
