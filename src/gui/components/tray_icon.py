import traceback
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QSystemTrayIcon

from src.gui.components.context_menu import ContextMenu
from src.utils import base64_to_icon


# Classe para o ícone do tray
class TrayIcon(QSystemTrayIcon):
    hide_signal = pyqtSignal()
    show_signal = pyqtSignal()

    def __init__(self, parent=None, icon_base64: str = None):
        super(TrayIcon, self).__init__(parent=parent)
        self.parent = parent
        self.menu = ContextMenu(parent=parent)

        if icon_base64:
            self.setIcon(base64_to_icon(icon_base64))

        self._set_signals()
        self.setContextMenu(self.menu)
        self.setVisible(True)

    def _set_signals(self):
        self.hide_signal.connect(self.parent.hide)
        self.show_signal.connect(self.parent.show)

        self.activated.connect(self._handle_tray_click)

    def _handle_tray_click(self, reason):
        if reason == self.Trigger:
            signal = self.hide_signal if self.parent.isVisible() else self.show_signal
            signal.emit()

    # TODO: CHANGE COLOR IF DEVICE IS CONNECTED WITH INDIVIDUAL DEVICE CONTROL
    # def tray_icon_controller():
    #     for device in DEVICES_MAPPING.values():
    #         if device.get("tray") and device.get("connected"):
    #             return True
    #     return False

    def exit(self):
        """Fecha o aplicativo."""
        try:
            QThread().quit()
            # self.parent.thread.quit()
            # self.thread.quit()  # Para a thread de forma segura
            # self.thread.wait()  # Aguarda que a thread termine
            # self.main_app.quit()  # Fecha o aplicativo
            # self.destroy()
            return True
        except:  # noqa
            pass
        print(f"Exit error: {traceback.format_exc()}")
        return None
