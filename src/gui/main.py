import subprocess
import threading
import time
import traceback

from evdev import InputDevice, list_devices
from PyQt5.QtCore import (
    QObject,
    QSize,
    Qt,
    QThread,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src import ALLOWED_DEVICES, DEVICES_MAPPING
from src.gui.tray_icon import TrayIcon, tray_icon_controller
from src.kodi_manager import KodiJsonRpc
from src.utils import (
    BUTTONS_ARRAY,
    are_processes_running,
    base64_to_icon,
)


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


class DeviceMonitor(QObject):
    pressed_hide_show = pyqtSignal()

    button_up = pyqtSignal()
    button_down = pyqtSignal()
    button_left = pyqtSignal()
    button_right = pyqtSignal()
    button_enter = pyqtSignal()

    connected = pyqtSignal()
    disconnected = pyqtSignal()

    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.monitored_devices = {}
        self.lock = threading.Lock()
        self.buttons = {
            x: {a: self.__getattribute__(b) for a, b in y.items() if isinstance(a, int)}
            for x, y in DEVICES_MAPPING.items()
        }

    def monitor_device(self, device_path):
        device = InputDevice(device_path)
        print(f"Monitorando eventos de: {device.name} ({device.path})")

        try:
            for event in device.read_loop():
                if any([x for x in are_processes_running().values()]):
                    continue
                if event.value == 1:
                    try:
                        action = self.buttons[device.name][event.code]
                        action.emit()
                        print(f"EVNT - {device.name} - {action}")
                    except:  # noqa
                        pass
        except OSError:
            pass
        except Exception:
            print(f"Erro ao monitorar {device.name}: {traceback.format_exc()}")
        finally:
            with self.lock:
                if device_path in self.monitored_devices:
                    del self.monitored_devices[device_path]
                    print(
                        f"Dispositivo removido do monitoramento: {device.name} ({device.path})"
                    )

    def refresh_devices(self):
        """
        Verifica dispositivos permitidos conectados e atualiza a lista monitorada.
        """
        allowed_devices = [
            dev
            for dev in [InputDevice(path) for path in list_devices()]
            if dev.name in ALLOWED_DEVICES
        ]
        with self.lock:
            # Adicionar novos dispositivos
            for device in allowed_devices:
                if device.path not in self.monitored_devices:
                    print(f"Novo dispositivo detectado: {device.name} ({device.path})")
                    DEVICES_MAPPING[device.name]["connected"] = True
                    DEVICES_MAPPING[device.name]["path"] = device.path
                    thread = threading.Thread(
                        target=self.monitor_device, args=(device.path,), daemon=True
                    )
                    self.monitored_devices[device.path] = thread
                    thread.start()
                    self.connected.emit()

            # Remover dispositivos desconectados
            monitored_paths = list(self.monitored_devices.keys())
            for path in monitored_paths:
                if path not in [device.path for device in allowed_devices]:
                    for device in DEVICES_MAPPING.values():
                        if DEVICES_MAPPING[device].get("path") == path:
                            print(f"Dispositivo desconectado: {path}")
                            DEVICES_MAPPING[InputDevice]["connected"] = False
                            del self.monitored_devices[path]
                            self.disconnected.emit()
        self.finished.emit()

    def start_monitoring(self):
        """
        Inicia o monitoramento contínuo para detectar dispositivos adicionados/removidos.
        """
        try:
            while True:
                self.refresh_devices()
                time.sleep(1)  # Atualiza a lista de dispositivos a cada segundo
        except KeyboardInterrupt:
            print("INFO - \nEncerrando monitoramento...")


class KodiMainWindow(QMainWindow):
    def __init__(self, main_app: QApplication):
        super(KodiMainWindow, self).__init__()
        self.thread = QThread()
        self.main_app = main_app
        self.kodi_api = KodiJsonRpc("localhost")

        self.buttons_carrousel = {}
        self.button_layout = None
        self.button_kodi = None
        self.button_emulationstation = None
        self.button_exit = None

        # ____ SET TRAY ICON ____
        self.tray_icon = TrayIcon()
        self.tray_icon.menu.close_signal.connect(self.close)
        self.tray_icon.hide_show_signal.connect(self.hide_show_tray)

        self.tray_icon.show()
        # ____ SET TRAY ICON ____

        # ____ SET DEVICE MONITOR ____
        self.device_monitor_worker = DeviceMonitor()
        self.device_monitor_worker.connected.connect(self.show)
        self.device_monitor_worker.connected.connect(self.switch_icon)
        self.device_monitor_worker.disconnected.connect(self.hide)
        self.device_monitor_worker.disconnected.connect(self.switch_icon)
        self.device_monitor_worker.pressed_hide_show.connect(self.hide_show_tray)

        # Conexões dos sinais
        self.device_monitor_worker.button_up.connect(self.on_up_left)
        self.device_monitor_worker.button_down.connect(self.on_down_right)
        self.device_monitor_worker.button_left.connect(self.on_up_left)
        self.device_monitor_worker.button_right.connect(self.on_down_right)
        self.device_monitor_worker.button_enter.connect(self.on_enter)

        self.device_monitor_worker.moveToThread(self.thread)
        self.device_monitor_worker.finished.connect(self.exit)

        # ____ SET DEVICE MONITOR ____

        # Sinais Worker e thread
        self.thread.started.connect(self.device_monitor_worker.start_monitoring)
        self.thread.finished.connect(self.thread.deleteLater)

        self.init_ui()
        self.thread.start()

    def init_ui(self):
        print("INFO - Iniciando interface gráfica...")
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
        self.button_kodi = self.create_button(self.open_kodi)
        self.button_kodi.setIcon(base64_to_icon(BUTTONS_ARRAY.get("kodi")))

        self.button_emulationstation = self.create_button(self.open_emulationstation)
        self.button_emulationstation.setIcon(
            base64_to_icon(BUTTONS_ARRAY.get("emulationstation"))
        )

        self.button_exit = self.create_button(self.hide)
        self.button_exit.setIcon(base64_to_icon(BUTTONS_ARRAY.get("exit")))

        self.buttons_carrousel.update(
            {
                0: self.button_kodi,
                1: self.button_emulationstation,
                2: self.button_exit,
            }
        )
        # Adiciona os botões ao layout
        self.button_layout.addWidget(self.button_kodi, alignment=Qt.AlignLeft)
        self.button_layout.addWidget(
            self.button_emulationstation, alignment=Qt.AlignCenter
        )
        self.button_layout.addWidget(self.button_exit, alignment=Qt.AlignRight)
        print("INFO - Interface gráfica iniciada com sucesso!")
        # Centralizar janela na tela
        self.center_on_screen()
        print("INFO - Janela centralizada na tela.")

    def create_button(self, action):
        button = CustomButton(
            button_style=self.create_button_style("#FFFFFFFF", "#0056b3")
        )
        button.clicked.connect(action)
        return button

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

    def center_on_screen(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def open_emulationstation(self):
        print("INFO - Abrindo EmulationStation...")
        self.hide()
        return subprocess.run(
            ["emulationstation"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.decode("utf-8")

    def open_kodi(self):
        print("INFO - Abrindo o Kodi...")
        self.hide()
        self.kodi_api.open_kodi()

    @staticmethod
    def on_enter():
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, QPushButton):
            focused_widget.click()

    def on_up_left(self):
        current_focus = QApplication.focusWidget()
        for index, btn in self.buttons_carrousel.items():
            if current_focus == btn:
                list(self.buttons_carrousel.values())[index - 1].setFocus()

    def on_down_right(self):
        current_focus = QApplication.focusWidget()
        for index, btn in self.buttons_carrousel.items():
            if current_focus == btn:
                try:
                    list(self.buttons_carrousel.values())[index + 1].setFocus()
                except IndexError:
                    list(self.buttons_carrousel.values())[0].setFocus()

    def switch_icon(self):
        self.tray_icon.setIcon(base64_to_icon(connected=tray_icon_controller()))

    def hide_show_tray(self):
        self.hide() if self.isVisible() else self.show()

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
