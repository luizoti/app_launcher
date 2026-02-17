import threading
import time
import traceback
import typing

from evdev import InputDevice, categorize, ecodes, list_devices
from PySide6.QtCore import QObject, Signal

from src.enums import actions_map, actions_map_reversed
from src.settings import SettingsManager, SettingsModel
from src.settings_model import MappingsModel


class DeviceMonitor(QObject):
    action = Signal(int)
    tray_action = Signal(str)

    def __init__(self, settings: SettingsModel = SettingsManager().get_settings()):
        super().__init__()
        self.lock = threading.Lock()
        self.settings = settings

        self.connected_devices = []
        self.event_mapping = {
            ecodes.EV_KEY: self._get_button_mapping,
            ecodes.EV_ABS: {
                ecodes.ABS_HAT0X: {-1: 3, 1: 4},
                ecodes.ABS_HAT0Y: {-1: 1, 1: 2},
            },
        }

    def _get_button_mapping(
        self, device_name=None, event=None
    ) -> typing.Optional[typing.Dict[typing.Text, int] | None]:
        if not device_name:
            raise TypeError("Argument `device_name` cannot None")
        if not event:
            raise TypeError("Argument `event` code cannot None")

        key_event = categorize(event)
        mappings: MappingsModel = getattr(
            getattr(self.settings.mappings, device_name), "buttons"
        )
        if key_event.keystate == 1:
            for action, event_code_int in mappings.model_dump(mode="python").items():
                if key_event.scancode == event_code_int:
                    return actions_map_reversed.get(action)
        return None

    def _get_allowed_devices(self):
        """
        Ger Allowed devices based on devices listed on settings.json mapping.
        """
        return (
            dev
            for dev in [InputDevice(path) for path in list_devices()]
            if dev.name in list(self.settings.mappings.keys())
        )

    def _monitor_device(self, device: InputDevice):
        print(f"INFO - Monitorando eventos de: {device.name} ({device.path})")
        try:
            for event in device.read_loop():
                try:
                    if hasattr(self.event_mapping.get(event.type), "__call__"):
                        command = self.event_mapping[event.type](
                            device_name=device.name, event=event
                        )
                    else:
                        command = self.event_mapping[event.type][event.code][
                            event.value
                        ]
                    if command:
                        try:
                            self.action.emit(command)
                            print(
                                f"EVNT - DEVICE: {device.name} | EV_CODE: {event.code} - ACTION: {actions_map.get(command)}"
                            )
                        except Exception:  # noqa
                            print(traceback.format_exc())
                        except ValueError as NotMappedEvent:  # noqa
                            print(NotMappedEvent)
                        continue
                    if event.type == 1 and event.value == 1:
                        print(f"INFO - Event code not mapped {event.code}")
                except (KeyError, AttributeError, TypeError):
                    pass
        except OSError:
            pass
        except Exception:
            print(f"ERROR - Erro ao monitorar {device.name}: {traceback.format_exc()}")
        finally:
            with self.lock:
                if device.path in self.connected_devices:
                    self.connected_devices.remove(device.path)
                    print(
                        f"INFO - Dispositivo removido do monitoramento: {device.name} ({device.path})"
                    )
                    self.tray_action.emit("disconnected")

    def _refresh_devices(self):
        """
        Verifica dispositivos permitidos conectados e atualiza a lista de dispositivos monitorados.
        """
        with self.lock:
            for device in self._get_allowed_devices():
                if device.path not in self.connected_devices:
                    print(
                        f"INFO - Novo dispositivo detectado: {device.name} ({device.path})"
                    )

                    device_model: MappingsModel = getattr(self.settings.mappings, device.name)

                    if device_model.tray:
                        self.tray_action.emit("connected")
                    thread = threading.Thread(
                        target=self._monitor_device, args=(device,), daemon=True
                    )
                    self.connected_devices.append(device.path)
                    thread.start()

    def start_monitor(self):
        """
        Inicia o monitoramento contínuo para detectar dispositivos adicionados/removidos.
        """
        try:
            while True:
                self._refresh_devices()
                time.sleep(1)  # Atualiza a lista de dispositivos a cada segundo
        except KeyboardInterrupt:
            print("INFO - \nEncerrando monitoramento...")
