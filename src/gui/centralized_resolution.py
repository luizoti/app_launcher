
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow


class CentralizedAppResolution:
    def __init__(self, app: QMainWindow):
        super(CentralizedAppResolution, self).__init__()
        application_primary_screen = QApplication.primaryScreen()
        if application_primary_screen:
            self.geometry: QRect = application_primary_screen.geometry()
        self.app = app

    def centralized_resolution(self) -> QPoint:
        width = (self.geometry.width() - self.app.width()) // 2
        height = (self.geometry.height() - self.app.height()) // 2
        return QPoint(width, height)
