from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QSystemTrayIcon

from src.gui.components.context_menu import ContextMenu
from src.gui.icons.cache_loader import get_icon
from src.settings import SettingsManager, SettingsModel


# Classe para o ícone do tray
class TrayIcon(QSystemTrayIcon):
    tray_action = Signal(str)

    def __init__(
        self,
        parent: QObject | None = None,
        settings: SettingsModel | None = None,
    ):
        super().__init__(parent=parent)
        self.settings = settings
        self.menu = ContextMenu()

        self.settings: SettingsModel = (
            settings if settings else SettingsManager().get_settings()
        )
        self.setIcon(get_icon(self.settings.tray.standby))

        self._set_signals()
        self.setContextMenu(self.menu)
        self.setVisible(True)

    def _on_toggle_visibility(self):
        """Callback para alternar a visibilidade da interface."""
        self.tray_action.emit("toggle_view")

    def _on_exit(self):
        """Callback para fechar a aplicação."""
        self.tray_action.emit("close")

    def _set_signals(self):
        self.activated.connect(self._handle_tray_click)

        if self.menu.change_visibility_action:
            self.menu.change_visibility_action.triggered.connect(
                self._on_toggle_visibility
            )

        if self.menu.exit_action:
            self.menu.exit_action.triggered.connect(self._on_exit)

    @Slot(QSystemTrayIcon.ActivationReason)
    def _handle_tray_click(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == self.ActivationReason.Trigger:
            self.tray_action.emit("toggle_view")

    @Slot(str)
    def handler_switch_icon(self, reason: str):
        if self.settings:
            self.setIcon(get_icon(getattr(self.settings.tray, reason)))
