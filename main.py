import os
import sys
from logging import Logger, getLogger

from PySide6.QtWidgets import QApplication

from src.gui.app import AppMainWindow
from src.instance import check_pid_exist, get_current_pid, read_pid_file, write_pid_file
from src.log import setup_logging

DEBUG_MODE = not getattr(sys, "frozen", False)
setup_logging(debug=DEBUG_MODE)
logger: Logger = getLogger(__name__)

os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

app = QApplication(sys.argv)
# app.setQuitOnLastWindowClosed(
#     True
# )  # Impede que o app feche quando a última janela for fechada

if __name__ == "__main__":
    loaded_pid: int = read_pid_file()
    if loaded_pid:
        if check_pid_exist(loaded_pid):
            logger.debug(
                f"Another instancie running with PID: {loaded_pid}",
            )
            sys.exit(1)
    logger.info(f"Started with PID: {get_current_pid()}")
    write_pid_file()
    app_window = AppMainWindow()
    app_window.show_ui()
    sys.exit(app.exec())
