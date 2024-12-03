import logging
import subprocess
import sys
import threading
import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
)
from systemd.journal import JournalHandler

from src.kodi_manager import KodiJsonRpc

# Configuração do log
logger = logging.getLogger("KodiJsonRpc")
logger.setLevel(logging.DEBUG)  # Define o nível de log
journal_handler = JournalHandler()  # Configura o journald como destino
journal_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(journal_handler)


# Console para debug adicional
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)


class KodiWidget(QWidget):
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


def monitor_controller(kodi_api):
    print("Iniciando monitor do controle!")
    controller_connected = True
    try:
        while True:
            connected = is_controller_connected()
            if not connected and controller_connected:
                print("Controller disconnected. Pausing Kodi...")
                kodi_api.pause()
                app = QApplication(sys.argv)
                window = KodiWidget(kodi_api)
                window.show()
                app.exec_()
            controller_connected = connected
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def is_controller_connected():
    try:
        result = subprocess.run(
            ["pgrep", "-f", "bluetoothd"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking controller connection: {e}")
        return False


class Task:
    """A simple class for performing a task."""

    def __init__(self, quit_flag, name=None, interval=1):
        if name is None:
            name = id(self)
        # Set up the task object
        self.quit_flag = quit_flag
        self.name = name
        self.interval = interval
        logging.debug("Task %s created" % self.name)

    def run(self):
        try:
            logging.debug("Task %s started" % self.name)
            while not self.quit_flag:
                logging.debug("Task %s is doing something" % self.name)
                monitor_controller(KodiJsonRpc("localhost"))
                time.sleep(self.interval)
        finally:
            logging.debug("Task %s performing cleanup..." % self.name)
            # Perform cleanup here
            logging.debug("Task %s stopped." % self.name)


class Flag(threading.Event):
    """A wrapper for the typical event class to allow for overriding the
    `__bool__` magic method, since it looks nicer.
    """

    def __bool__(self):
        return self.is_set()


if __name__ == "__main__":
    flag = Flag()
    # Create some tasks
    task = Task(flag, name="Task Started :)")
    # Create some threads
    thread = threading.Thread(target=task.run, name=task.name)
    try:
        # Create the event flag for when we wish to terminate.
        # Start the threads
        thread.start()
        # Spin in place while threads do their work
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Interrupt received, setting quit flag.")
        flag.set()
        sys.exit(0)
