
import logging

from PySide6.QtCore import Signal, Slot

from src.enums import actions_map

logger = logging.getLogger(__name__)


class ActionManager:
    actions = Signal(int)

    @Slot(int, name="action_handler")
    def action_handler(self, action_id: int) -> None:
        method_name = actions_map.get(action_id)
        if not method_name:
            return
        method = getattr(self, method_name, None)
        if callable(method):
            method()
            return
        logger.error(f"Erro: Método {method_name} não encontrado em {self.__class__.__name__}")
