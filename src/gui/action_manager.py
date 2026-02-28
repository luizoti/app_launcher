
import logging

from PySide6.QtCore import Signal, Slot

logger = logging.getLogger(__name__)


class ActionManager:
    actions = Signal(str)

    @Slot(str, name="action_handler", result=None)
    def action_handler(self, action_name: str) -> None:
        method = getattr(self, action_name, None)
        if callable(method):
            method()
        return
