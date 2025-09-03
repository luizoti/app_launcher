from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

from src.enums import actions_map


class ActionManager:
    actions = pyqtSignal(int)

    @QtCore.pyqtSlot(int, name="action_handler")
    def action_handler(self, action: int = None):
        if not action:
            raise TypeError("Argument `action` cannot be None")
        try:
            getattr(self, actions_map.get(action))()
        except AttributeError:
            pass
