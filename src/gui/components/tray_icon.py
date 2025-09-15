from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSystemTrayIcon

from src.enums import actions_map_reversed
from src.gui.components.context_menu import ContextMenu
from src.settings import SettingsManager
from src.utils import build_icon


# Classe para o ícone do tray
class TrayIcon(QSystemTrayIcon):
    tray_action = pyqtSignal(int)

    def __init__(self, parent=None, icon_base64: str = None):
        super(TrayIcon, self).__init__(parent=parent)
        self.menu = ContextMenu()

        self.setIcon(build_icon(self.settings.get("tray").get("icons").get("standby")))

        self._set_signals()
        self.setContextMenu(self.menu)
        self.setVisible(True)

    def _set_signals(self):
        self.activated.connect(self._handle_tray_click)

        self.menu.change_visibility_action.triggered.connect(
            lambda x: self.tray_action.emit(actions_map_reversed.get("toggle_view"))
        )
        self.menu.exit_action.triggered.connect(
            lambda x: self.tray_action.emit(actions_map_reversed.get("close"))
        )

    def _handle_tray_click(self, reason):
        if reason == self.Trigger:
            self.tray_action.emit(actions_map_reversed.get("toggle_view"))

    # TODO: CHANGE COLOR IF DEVICE IS CONNECTED WITH INDIVIDUAL DEVICE CONTROL
    # def tray_icon_controller():
    #     for device in DEVICES_MAPPING.values():
    #         if device.get("tray") and device.get("connected"):
    #             return True
    #     return False
