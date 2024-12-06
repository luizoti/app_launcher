import os
import sys

from PyQt5.QtWidgets import QApplication

from src.gui.main import KodiMainWindow

os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

# Configuração do aplicativo
app = QApplication(sys.argv)
# app.setQuitOnLastWindowClosed(
#     True
# )  # Impede que o app feche quando a última janela for fechada

if __name__ == "__main__":
    window = KodiMainWindow(main_app=app)
    window.hide()
    sys.exit(app.exec_())
