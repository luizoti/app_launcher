from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu

from src.utils import base64_to_icon, is_controller_connected


class ContextMenu(QMenu):
    close_signal = pyqtSignal()
    hide_show_signal = pyqtSignal()

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super(ContextMenu, self).__init__(*args, **kwargs)

        hide_show_button = self.addAction("Hide/Show")
        hide_show_button.triggered.connect(self.hide_show_button)

        exit_action = self.addAction("Exit")
        exit_action.triggered.connect(self.emit_close_signal)

    def hide_show_button(self):
        self.hide_show_signal.emit()

    def emit_close_signal(self):
        """Emite o sinal de fechar."""
        self.close_signal.emit()


# Classe para o ícone do tray
class TrayIcon(QSystemTrayIcon):
    hide_show_signal = pyqtSignal()

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super(TrayIcon, self).__init__(*args, **kwargs)
        self.activated.connect(self.left_click_action)
        self.setIcon(base64_to_icon(connected=is_controller_connected()))
        self.setVisible(True)

        # Set tray context menu
        self.menu = ContextMenu()
        self.setContextMenu(self.menu)

    def left_click_action(self, reason):
        if reason == self.Trigger:
            self.hide_show_signal.emit()
