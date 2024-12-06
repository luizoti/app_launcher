import traceback
from datetime import datetime, timedelta
from time import sleep

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from pynput import keyboard

from src.gui.tray_icon import TrayIcon
from src.kodi_manager import KodiJsonRpc
from src.utils import is_controller_connected, base64_to_icon

KODI_API = KodiJsonRpc("localhost")


class CustomButton(QPushButton):
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return]:  # Código da tecla Enter
            self.click()  # Emula o clique do botão
        else:
            super().keyPressEvent(event)  # Processa outros eventos normalmente


class KeyboardMonitorWorker(QObject):
    pressed_hide_show = pyqtSignal()

    def run(self):
        """Tarefa longa que será executada em thread separada."""
        try:
            # Listener para eventos de teclado
            with keyboard.Listener(on_press=self.on_press) as listener:
                print("Pressione qualquer tecla. Pressione ESC para sair.")
                listener.join()
        except KeyboardInterrupt:
            return None
        # finally:
        #     self.finished.emit()

    def on_press(self, key):
        try:
            if key.char == "p":
                self.pressed_hide_show.emit()
        except AttributeError:
            pass


# Worker para tarefas longas
class KodiMonitorWorker(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    finished = pyqtSignal()

    def run(self):
        """Tarefa longa que será executada em thread separada."""
        connected = False
        try:
            while True:
                is_connected = is_controller_connected()
                sleep(1)
                if is_connected and connected is False:
                    connected = True
                    print("Controle conectado. Abrir Kodi?")
                    self.connected.emit()
                elif not is_connected and connected is True:
                    connected = False
                    print("Controller disconnected. Pausing Kodi...")
                    self.disconnected.emit()
        except KeyboardInterrupt:
            return None
        finally:
            self.finished.emit()


class KodiMainWindow(QMainWindow):
    def __init__(self, main_app: QApplication):
        super(KodiMainWindow, self).__init__()
        self.main_app = main_app

        self.thread = QThread()
        self.thread2 = QThread()
        self.kodi_worker = KodiMonitorWorker()
        self.keyboard_worker = KeyboardMonitorWorker()

        self.tray_icon = TrayIcon()
        self.tray_icon.show()
        # Sinais Tray
        self.tray_icon.menu.close_signal.connect(self.close)
        self.tray_icon.hide_show_signal.connect(self.hide_show)
        self.kodi_worker.moveToThread(self.thread)
        self.keyboard_worker.moveToThread(self.thread2)

        # Sinais Worker e thread
        self.thread.started.connect(self.kodi_worker.run)
        self.thread2.started.connect(self.keyboard_worker.run)
        self.kodi_worker.finished.connect(self.close)

        self.thread.finished.connect(self.thread.deleteLater)

        self.kodi_worker.connected.connect(self.show)
        self.kodi_worker.connected.connect(self.switch_icon)
        self.kodi_worker.disconnected.connect(self.hide)
        self.kodi_worker.disconnected.connect(self.switch_icon)

        self.keyboard_worker.pressed_hide_show.connect(self.hide_show)

        self.init_ui()
        self.thread.start()
        self.thread2.start()

    def switch_icon(self):
        self.tray_icon.setIcon(base64_to_icon(connected=is_controller_connected()))

    def hide_show(self):
        if self.isVisible():
            self.hide()
            return True
        self.show()

    def exit(self):
        """Fecha o aplicativo."""
        try:
            self.thread.quit()  # Para a thread de forma segura
            self.thread.wait()  # Aguarda que a thread termine
            self.main_app.quit()  # Fecha o aplicativo
            self.destroy()
            return True
        except:
            pass
        print(f"Exit error: {traceback.format_exc()}")

    def init_ui(self):
        # Remover decorações da janela
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(400, 200)  # Tamanho fixo para a janela

        # Criar widget central
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout e widgets
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)

        # Texto da pergunta
        question_label = QLabel("Abrir o Kodi?")
        question_label.setAlignment(Qt.AlignCenter)
        question_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(question_label)

        # Layout para os botões
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Botão "Sim"
        btn_yes = CustomButton("Sim")
        btn_yes.setStyleSheet(
            """
            QPushButton {
                font-size: 20px; 
                padding: 10px; 
                background-color: #28a745; 
                color: white; 
                border: none; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:focus {
                outline: 2px solid #005cbf;
            }
        """
        )
        btn_yes.clicked.connect(self.open_kodi)
        button_layout.addWidget(btn_yes)

        # Botão "Não"
        btn_no = CustomButton("Não")
        btn_no.setStyleSheet(
            """
            QPushButton {
                font-size: 20px; 
                padding: 10px; 
                background-color: #dc3545; 
                color: white; 
                border: none; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:focus {
                outline: 2px solid #005cbf;
            }
        """
        )
        btn_no.clicked.connect(self.hide)
        button_layout.addWidget(btn_no)

        # Centralizar janela na tela
        self.center_on_screen()

    def center_on_screen(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def open_kodi(self):
        print("Abrindo o Kodi...")
        self.hide()
        KODI_API.open_kodi()

    def restart_kodi(self):
        print("Restart kodi...")
        timeout = datetime.now() + timedelta(minutes=5)
        current_playing = KODI_API.get_currently_playing()
        KODI_API.pause()
        KODI_API.stop()
        KODI_API.quit()
        sleep(3)
        KODI_API.open_kodi()
        while not KODI_API.is_kodi_running():
            if datetime.now() > timeout:
                break
            try:
                KODI_API.play_content(**current_playing)
                sleep(1)
            except Exception as Err:
                print(f"Tentativa de reiniciar reprodução: {Err}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # Código da tecla Enter
            self.hide()  # Emula o clique do botão
            return
        super().keyPressEvent(event)
