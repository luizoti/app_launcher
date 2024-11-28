import sys
import subprocess
import time
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
import requests

from kodi_manager import KodiJsonRpc

class KodiManager(QWidget):
    def __init__(self, kodi):
        super().__init__()
        self.kodi = kodi
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Reabrir Kodi?")
        self.setGeometry(100, 100, 300, 150)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        label = QLabel("O controle desconectou. Deseja reabrir o Kodi?")
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        yes_button = QPushButton("Sim")
        no_button = QPushButton("Não")
        yes_button.clicked.connect(self.on_yes)
        no_button.clicked.connect(self.on_no)
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def on_yes(self):
        self.kodi.open_kodi()
        self.close()

    def on_no(self):
        self.close()


def monitor_controller(kodi):
    print("Iniciando monitor do controle!")
    controller_connected = True

    while True:
        connected = is_controller_connected()
        if not connected and controller_connected:
            print("Controller disconnected. Pausing Kodi...")
            kodi.pause()
            app = QApplication(sys.argv)
            window = KodiManager(kodi)
            window.show()
            app.exec_()
        controller_connected = connected
        time.sleep(1)


def is_controller_connected():
    try:
        result = subprocess.run(["pgrep", "-f", "bluetoothd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking controller connection: {e}")
        return False


if __name__ == "__main__":
    kodi = KodiJsonRpc("localhost")  # Substitua pelo IP do seu Kodi
    thread = threading.Thread(target=monitor_controller, args=(kodi,), daemon=True)
    thread.start()
    thread.join()
