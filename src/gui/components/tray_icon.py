from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSystemTrayIcon

from src.enums import actions_map_reversed
from src.gui.components.context_menu import ContextMenu
from src.settings import SettingsManager
from src.utils import build_icon


# Classe para o ícone do tray
class TrayIcon(QSystemTrayIcon):
    tray_action = pyqtSignal(int)

    def __init__(self, parent=None, settings=SettingsManager().get_settings()):
        super(TrayIcon, self).__init__(parent=parent)
        self.settings = settings
        self.menu = ContextMenu()

        self.setIcon(build_icon(self.settings.get("tray").get("icons").get("standby")))

        self._set_signals()
        self.setContextMenu(self.menu)
        self.setVisible(True)

    def _on_toggle_visibility(self):
        """Callback para alternar a visibilidade da interface."""
        self.tray_action.emit(actions_map_reversed.get("toggle_view"))

    def _on_exit(self):
        """Callback para fechar a aplicação."""
        self.tray_action.emit(actions_map_reversed.get("close"))


    def _set_signals(self):
        self.activated.connect(self._handle_tray_click)
        self.menu.change_visibility_action

        if self.menu.change_visibility_action:
            self.menu.change_visibility_action.triggered.connect(
                self._on_toggle_visibility
            )

        if self.menu.exit_action: 
            self.menu.exit_action.triggered.connect(
               self._on_exit
            )

    @pyqtSlot(QSystemTrayIcon.ActivationReason)
    def _handle_tray_click(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == self.ActivationReason.Trigger:
            self.tray_action.emit(actions_map_reversed.get("toggle_view"))
 
    @pyqtSlot(str)
    def handler_switch_icon(self, reason: typing.Text):
        self.setIcon(build_icon(getattr(self.settings.tray, reason)))
