import time

import threading
import traceback
from PyQt5.QtCore import QObject, pyqtSignal
from evdev import InputDevice, list_devices

from src.settings import DEVICES_MAPPING, ALLOWED_DEVICES
from src.utils import are_processes_running


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
