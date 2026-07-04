from src.settings import get_settings
from src.utils import check_running_processes


class ActionManager:
    @staticmethod
    def _is_blocked() -> bool:
        block_list = get_settings().block_if_running
        if block_list:
            running = check_running_processes(block_list)
            if running:
                return True
        return False
