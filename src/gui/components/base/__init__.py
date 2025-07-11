from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon
from PyQt5.QtWidgets import QMenu

from src.settings import SettingsManager


class AppMainWindowTyped(QMainWindow):
    def __init__(self, main_app: QApplication, settings=SettingsManager):
        super(AppMainWindowTyped, self).__init__()
        self.settings = settings
        self.main_app = main_app
        self.thread: QThread()


class TrayIconTyped(QSystemTrayIcon):
    hide_signal = pyqtSignal()
    show_signal = pyqtSignal()

    def __init__(self, parent: AppMainWindowTyped):
        super(TrayIconTyped, self).__init__(parent)
        self.parent = parent


class ContextMenuTyped(QMenu):
    close_signal = pyqtSignal()
    hide_signal = pyqtSignal()
    show_signal = pyqtSignal()

    def __init__(self, parent: TrayIconTyped = None, *args, **kwargs):
        super(ContextMenuTyped, self).__init__(*args, **kwargs)
        self.parent = parent

    def hide_show_button(self):
        ...

    def emit_close_signal(self):
        """Emite o sinal de fechar."""
        self.close_signal.emit()
