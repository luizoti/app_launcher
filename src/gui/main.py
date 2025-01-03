import subprocess
import traceback
from datetime import datetime, timedelta
from time import sleep

import pygame
from PyQt5.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
    QObject,
    QSize,
)
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
from src.utils import (
    is_controller_connected,
    base64_to_icon,
    BUTTONS_ARRAY,
    are_processes_running,
)

KODI_API = KodiJsonRpc("localhost")


class CustomButton(QPushButton):
    def __init__(self, button_style=None):
        super().__init__()
        self.setIcon(base64_to_icon(icon=BUTTONS_ARRAY.get("tray").get("connected")))
        self.setIconSize(QSize(100, 100))
        self.setMinimumSize(120, 120)
        self.setMaximumSize(120, 120)
        self.setStyleSheet(button_style)

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return]:  # Código da tecla Enter
            self.click()  # Emula o clique do botão
        else:
            super().keyPressEvent(event)  # Processa outros eventos normalmente


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


class JoyStickMonitorWorker(QObject):
    button_up = pyqtSignal()
    button_down = pyqtSignal()
    button_left = pyqtSignal()
    button_right = pyqtSignal()
    button_enter = pyqtSignal()
    pressed_hide_show = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.joysticks = {}  # Armazena os joysticks conectados
        self.buttons = {
            4: self.button_up.emit,  # Botão "up"
            6: self.button_down.emit,  # Botão "down"
            7: self.button_left.emit,  # Botão "left"
            5: self.button_right.emit,  # Botão "right"
            14: self.button_enter.emit,  # Botão "X" como "enter"
            16: self.pressed_hide_show.emit,  # Botão "SHARE" como "enter"
        }

    def run(self):
        """Inicia o monitoramento do joystick."""
        pygame.init()
        pygame.joystick.init()
        print("Monitor de joystick iniciado.")
        self._initialize_joysticks()

        while self.running:
            if are_processes_running():
                try:
                    self._remove_joystick()
                except:
                    pass
                continue
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    try:
                        pressed_button = self.buttons[event.button]
                        pressed_button()
                    except (KeyError, TypeError):
                        pass
                    continue
                if event.type == pygame.JOYDEVICEADDED:
                    self._add_joystick(event.device_index)
                elif event.type == pygame.JOYDEVICEREMOVED:
                    self._remove_joystick(event.instance_id)

    def stop(self):
        """Interrompe o monitoramento."""
        self.running = False
        pygame.quit()
        print("Monitor de joystick parado.")

    def _initialize_joysticks(self):
        """Inicializa os joysticks conectados no início."""
        for i in range(pygame.joystick.get_count()):
            self._add_joystick(i)

    def _add_joystick(self, device_index):
        """Adiciona um joystick."""
        joystick = pygame.joystick.Joystick(device_index)
        joystick.init()
        self.joysticks[joystick.get_instance_id()] = joystick
        print(
            f"Joystick conectado: {joystick.get_name()} (ID: {joystick.get_instance_id()})"
        )

    def _remove_joystick(self, instance_id):
        """Remove um joystick desconectado."""
        if instance_id in self.joysticks:
            print(
                f"Joystick desconectado: {self.joysticks[instance_id].get_name()} (ID: {instance_id})"
            )
            del self.joysticks[instance_id]


class KeyboardMonitorWorker(QObject):
    pressed_hide_show = pyqtSignal()

    def run(self):
        """Tarefa longa que será executada em thread separada."""
        try:
            with keyboard.Listener(on_press=self.on_press) as listener:
                print("Pressione qualquer tecla. Pressione ESC para sair.")
                listener.join()
        except KeyboardInterrupt:
            return None
        # finally:
        #     self.finished.emit()

    def on_press(self, key):
        try:
            if not are_processes_running():
                if key == keyboard.Key.esc:
                    self.pressed_hide_show.emit()
        except AttributeError:
            pass


class KodiMainWindow(QMainWindow):
    def __init__(self, main_app: QApplication):
        super(KodiMainWindow, self).__init__()
        self.button_layout = None
        self.btn_carrousel = {}
        self.btn_kodi = None
        self.btn_emulationstation = None
        self.btn_exit = None

        self.main_app = main_app

        self.thread = QThread()
        self.thread2 = QThread()
        self.thread3 = QThread()

        self.kodi_worker = KodiMonitorWorker()
        self.keyboard_worker = KeyboardMonitorWorker()
        self.joystick_worker = JoyStickMonitorWorker()

        self.tray_icon = TrayIcon()
        self.tray_icon.show()

        # Sinais Tray
        self.tray_icon.menu.close_signal.connect(self.close)
        self.tray_icon.hide_show_signal.connect(self.hide_show_tray)
        self.kodi_worker.moveToThread(self.thread)
        self.keyboard_worker.moveToThread(self.thread2)
        self.joystick_worker.moveToThread(self.thread3)

        # Sinais Worker e thread
        self.thread.started.connect(self.kodi_worker.run)
        self.thread2.started.connect(self.keyboard_worker.run)
        self.thread3.started.connect(self.joystick_worker.run)
        self.kodi_worker.finished.connect(self.close)

        self.thread.finished.connect(self.thread.deleteLater)

        self.kodi_worker.connected.connect(self.show)
        self.kodi_worker.connected.connect(self.switch_icon)
        self.kodi_worker.disconnected.connect(self.hide)
        self.kodi_worker.disconnected.connect(self.switch_icon)

        self.keyboard_worker.pressed_hide_show.connect(self.hide_show_tray)
        self.joystick_worker.pressed_hide_show.connect(self.hide_show_tray)

        # Conexões dos sinais
        self.joystick_worker.button_up.connect(self.on_up_left)
        self.joystick_worker.button_down.connect(self.on_down_right)
        self.joystick_worker.button_left.connect(self.on_up_left)
        self.joystick_worker.button_right.connect(self.on_down_right)
        self.joystick_worker.button_enter.connect(self.on_enter)

        self.init_ui()
        self.thread.start()
        self.thread2.start()
        self.thread3.start()

    def init_ui(self):
        # Remover decorações da janela
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setFixedSize(500, 300)

        # Criar widget central
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #121212;")

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)

        # Header (Título)
        header_label = QLabel("Escolha uma aplicação para abrir:")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF;"
        )
        main_layout.addWidget(header_label)

        # Layout para os botões principais
        self.button_layout = QHBoxLayout()
        main_layout.addLayout(self.button_layout)

        # Botões para adicionar ao layout
        self.btn_kodi = self.create_button(self.open_kodi)
        self.btn_kodi.setIcon(base64_to_icon(BUTTONS_ARRAY.get("kodi")))

        self.btn_emulationstation = self.create_button(self.open_emulationstation)
        self.btn_emulationstation.setIcon(
            base64_to_icon(BUTTONS_ARRAY.get("emulationstation"))
        )

        self.btn_exit = self.create_button(self.hide)
        self.btn_exit.setIcon(base64_to_icon(BUTTONS_ARRAY.get("exit")))

        self.btn_carrousel.update(
            {
                0: self.btn_kodi,
                1: self.btn_emulationstation,
                2: self.btn_exit,
            }
        )
        # Adiciona os botões ao layout
        self.button_layout.addWidget(self.btn_kodi, alignment=Qt.AlignLeft)
        self.button_layout.addWidget(
            self.btn_emulationstation, alignment=Qt.AlignCenter
        )
        self.button_layout.addWidget(self.btn_exit, alignment=Qt.AlignRight)

        # Centralizar janela na tela
        self.center_on_screen()

    def create_button(self, action):
        button = CustomButton(
            button_style=self.create_button_style("#FFFFFFFF", "#0056b3")
        )
        button.clicked.connect(action)
        return button

    def open_emulationstation(self):
        print("Abrindo EmulationStation...")
        self.hide()
        result = subprocess.run(
            ["emulationstation"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode("utf-8")

    def center_on_screen(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    @staticmethod
    def create_button_style(
        color="#333333", hover_color="#444444", text_color="#FFFFFF"
    ):
        return f"""
        QPushButton {{
            font-size: 18px;
            background-color: {color};
            color: {text_color};
            border: 2px solid #555555;
            border-radius: 15px;
            padding: 10px;
            width: 120px;
            height: 120px;
            text-align: center;
        }}
        QPushButton:hover, QPushButton:focus {{
            background-color: {hover_color};
            outline: none;
            border-color: #888888;
        }}
        """

    def on_up_left(self):
        current_focus = QApplication.focusWidget()
        for index, btn in self.btn_carrousel.items():
            if current_focus == btn:
                list(self.btn_carrousel.values())[index - 1].setFocus()

    def on_down_right(self):
        current_focus = QApplication.focusWidget()
        for index, btn in self.btn_carrousel.items():
            if current_focus == btn:
                try:
                    list(self.btn_carrousel.values())[index + 1].setFocus()
                except IndexError:
                    list(self.btn_carrousel.values())[0].setFocus()

    @staticmethod
    def on_enter():
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, QPushButton):
            focused_widget.click()

    def hide_show(self):
        if self.isVisible():
            self.hide()
            return True
        self.show()

    def switch_icon(self):
        self.tray_icon.setIcon(base64_to_icon(connected=is_controller_connected()))

    def hide_show_tray(self):
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
        except:  # noqa
            pass
        print(f"Exit error: {traceback.format_exc()}")

    def open_kodi(self):
        print("Abrindo o Kodi...")
        self.hide()
        KODI_API.open_kodi()

    @staticmethod
    def restart_kodi():
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
