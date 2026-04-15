import os
import signal
import sys
from logging import Logger, getLogger

from PySide6.QtWidgets import QApplication

from src.gui.app import AppMainWindow
from src.instance import (
    check_pid_exist,
    destroy_pid_file,
    get_current_pid,
    read_pid_file,
    write_pid_file,
)
from src.log import setup_logging

DEBUG_MODE = not getattr(sys, "frozen", False)
setup_logging(debug=DEBUG_MODE)
logger: Logger = getLogger(__name__)

os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

app = QApplication(sys.argv)


def signal_handler(signum, frame):
    """Handle Ctrl+C to gracefully shutdown the app."""
    logger.info("Received interrupt signal, shutting down...")
    destroy_pid_file()
    app.quit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

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
