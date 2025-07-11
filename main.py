import os
import sys

import os
from PyQt5.QtWidgets import QApplication

from src.gui.app import AppMainWindow

os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

app = QApplication(sys.argv)
# app.setQuitOnLastWindowClosed(
#     True
# )  # Impede que o app feche quando a última janela for fechada

if __name__ == "__main__":
    app_window = AppMainWindow()
    app_window.show_ui()
    print("INFO - App started")
    sys.exit(app.exec_())
