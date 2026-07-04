import logging

from PySide6.QtCore import Signal, Slot

from src.settings import get_settings
from src.utils import check_running_processes

logger = logging.getLogger(__name__)


class ActionManager:
    actions = Signal(str)

    @staticmethod
    def _is_blocked() -> bool:
        block_list = get_settings().block_if_running
        if block_list:
            running = check_running_processes(block_list)
            if running:
                return True
        return False

    @Slot(str, name="action_handler", result=None)
    def action_handler(self, action_name: str) -> None:
        if self._is_blocked():
            logger.debug(f"ActionManager.action_handler: blocked ({action_name})")
            return

        method = getattr(self, action_name, None)
        if callable(method):
            method()
