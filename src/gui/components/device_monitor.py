import logging
import typing
from typing import cast

import pyudev  # type: ignore
from evdev import ecodes
from evdev.device import InputDevice
from evdev.util import categorize, list_devices  # type: ignore
from PySide6.QtCore import QObject, QRunnable, QThread, QThreadPool, Signal, Slot
from pyudev.pyside6 import MonitorObserver  # type: ignore

from src.settings import Settings, get_settings
from src.types.protocols.device import (
    InputDeviceEvDevProtocol,
    InputDevicePyDevProtocol,
    InputEventProtocol,
    KeyEventProtocol,
)
from src.types.schemas import DeviceMappingsModel

logger: logging.Logger = logging.getLogger(__name__)
settings: Settings = get_settings()


class Signals(QObject):
    started = Signal(str)
    completed = Signal(str)

    action = Signal(str)
    tray_action = Signal(str)
    connection_status = Signal(str)


class DeviceEventWorker(QRunnable):
    def __init__(
        self,
        input_device: InputDeviceEvDevProtocol,
    ) -> None:
        super().__init__()
        self.input_device: InputDeviceEvDevProtocol = input_device
        self.signals = Signals()

    def get_device_settings(self, event: InputEventProtocol) -> dict[
        int,
        typing.Callable[[typing.Any], None] | typing.Any | dict[int, int],
    ]:
        return {
            ecodes.EV_KEY: self._get_device_mapping(event=event),  # type: ignore
            ecodes.EV_ABS: {  # type: ignore
                ecodes.ABS_HAT0X: {-1: "left", 1: "right"},  # type: ignore
                ecodes.ABS_HAT0Y: {-1: "up", 1: "down"},  # type: ignore
            },
        }

    def _get_device_mapping(self, event: InputEventProtocol) -> int | None:
        key_event = cast(InputEventProtocol | KeyEventProtocol, categorize(event))
        device_mappings: DeviceMappingsModel | None = settings.mappings.get(
            self.input_device.name
        )
        if not device_mappings:
            logger.warning(f"No mapping found for device: {self.input_device.name}")
            return None
        try:
            if key_event.keystate != 1:
                return None
            key_scancode = key_event.scancode
            event_code = str(event.code)

            # Try both string and integer keys
            action = device_mappings.buttons.get(event_code)
            if action is None:
                try:
                    action = device_mappings.buttons.get(int(event_code))
                except (ValueError, TypeError):
                    pass

            logger.debug(
                f"event_code={event_code}, key_scancode={key_scancode}, "
                f"action={action}, device={self.input_device.name}"
            )
            return action
        except AttributeError:
            pass
        return None

    @Slot()
    def run(self):
        logger.debug(f"Worker thread: {QThread.currentThread()}")
        self.signals.started.emit(self.input_device.path)
        emit_action = self.signals.action.emit
        get_mappings = self.get_device_settings
        logger.info(f"[DeviceEventWorker] Started for: {self.input_device.name}")
        try:
            event: InputEventProtocol
            for event in self.input_device.read_loop():
                if event.type not in [ecodes.EV_KEY, ecodes.EV_ABS]:
                    continue
                mapping = get_mappings(event=event).get(event.type)
                if mapping is not None:
                    if isinstance(mapping, dict):
                        dpad = mapping.get(event.code)
                        if dpad:
                            direction = dpad.get(event.value)
                            if direction is not None:
                                logger.debug(f"[ACTION] {direction} emitted")
                                emit_action(direction)
                    else:
                        logger.debug(f"[ACTION] {mapping} emitted")
                        emit_action(mapping)
        except OSError:
            logger.warning(f"Device disconnected: {self.input_device.path}")
        self.signals.completed.emit(self.input_device.path)


class DeviceMonitor(QObject):
    action = Signal(str)
    tray_action = Signal(str)
    connection_status = Signal(str)

    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool().globalInstance()
        self.connected_devices: list[str] = []

        self._print_detected()
        logger.debug("--------------------------------")
        self._print_allowed()
        self._check_connection_status()

    @Slot()
    def start_monitor(self):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem="input")
        self.observer = MonitorObserver(self.monitor)
        self.observer.deviceEvent.connect(self._refresh_devices)
        logger.info("Device monitor started")
        try:
            self.monitor.start()
            logger.info("udev netlink monitor started successfully")
        except Exception as e:
            logger.error(f"Failed to start udev monitor: {e}")
        self._get_devices_on_start()

    def _print_detected(self) -> None:
        logger.info("=== DETECTED DEVICES ===")
        devices = (
            cast(InputDeviceEvDevProtocol, InputDevice(path))
            for path in cast(list[str], list_devices())
        )
        for item in devices:  # type: ignore
            logger.info(f"  - {item.name} | {item.path}")
        logger.info("=========================")

    def _print_allowed(self) -> None:
        logger.info("=== ALLOWED DEVICES (mappings) ===")
        for item in settings.mappings:
            logger.info(f"  - {item}")
        logger.info("==================================")

    def _check_connection_status(self) -> None:
        has_connected = False
        for device_name in settings.mappings:
            mappings = settings.mappings[device_name]
            if mappings.tray and device_name in self._get_connected_device_names():
                has_connected = True
                break

        status = "connected" if has_connected else "disconnected"
        self.connection_status.emit(status)
        logger.debug(f"Connection status: {status}")

    def _get_connected_device_names(self) -> set[str]:
        return {InputDevice(path).name for path in self.connected_devices}

    def _valid_device(self, device_path: str) -> InputDeviceEvDevProtocol | None:
        """

        Check if device is valid, filtering by /dev/input/event and
        verifying existence on settings.mappings.
        """
        if not device_path.startswith("/dev/input/event"):
            return None
        input_device = cast(InputDeviceEvDevProtocol, InputDevice(device_path))
        if input_device.name in settings.mappings:
            return input_device

    def _get_device_mappings(self, device_name: str) -> DeviceMappingsModel | None:
        return settings.mappings.get(device_name, None)

    def _get_devices_on_start(self) -> None:
        for device_path in list_devices():  # type: ignore
            valid_device = self._valid_device(device_path=device_path)  # type: ignore
            if not valid_device:
                continue
            self.create_new_treaded_device(valid_device)
            logger.info(f"Device connected: {(valid_device,)}")
        return None

    def create_new_treaded_device(self, input_device: InputDeviceEvDevProtocol):
        worker = DeviceEventWorker(input_device)
        worker.signals.action.connect(self.action.emit)
        self.thread_pool.start(worker)

    def _refresh_devices(self, device: InputDevicePyDevProtocol) -> None:
        device_action = device.action
        device_name = (
            device.get("ID_MODEL")
            or device.get("NAME")
            or device.get("PHYS")
            or "Unknown Device"
        )
        device_path: str | None = device.device_node

        logger.debug(
            f"Hotplug event: action={device_action}, device={device_name}, "
            f"path={device_path}"
        )

        if not device_path:
            logger.warning(f"Hotplug event received but no device_node: {device}")
            return

        if device_action == "add":
            if device_path in self.connected_devices:
                logger.debug(f"Device already tracked: {device_path}")
                return
            try:
                input_device: InputDeviceEvDevProtocol = self._valid_device(device_path)
            except Exception as e:
                logger.error(f"Failed to open device {device_path}: {e}")
                return
            if not input_device:
                logger.debug(f"Device not in mappings: {device_path} ({device_name})")
                return
            if input_device.name in settings.mappings:
                self.connected_devices.append(input_device.path)
                self.create_new_treaded_device(input_device)
                logger.info(f"Device connected: {input_device.name} ({device_path})")
                self.tray_action.emit("connected")
                self._check_connection_status()
            else:
                logger.debug(f"Device not in settings.mappings: {input_device.name}")
        elif device_action == "remove":
            if device_path in self.connected_devices:
                self.connected_devices.remove(device_path)
                logger.info(f"Device removed: {device_name} ({device_path})")
                self.tray_action.emit("disconnected")
                self._check_connection_status()
            else:
                logger.debug(f"Device not in tracked list: {device_path}")
