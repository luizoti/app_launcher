import os
import sys

from PyQt5.QtWidgets import QApplication

from src.gui.app import AppMainWindow
from src.insancie import read_pid_file, write_pid_file, check_pid_exist, get_current_pid

os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

app = QApplication(sys.argv)
# app.setQuitOnLastWindowClosed(
#     True
# )  # Impede que o app feche quando a última janela for fechada

if __name__ == "__main__":
    loaded_pid = read_pid_file()
    if loaded_pid:
        if check_pid_exist(loaded_pid):
            print("DEBUG - Another instancie running with PID:", loaded_pid)
            sys.exit(1)
    print("INFO - Started with PID:", get_current_pid())
    write_pid_file()
    app_window = AppMainWindow()
    app_window.show_ui()
    sys.exit(app.exec_())
