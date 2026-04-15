"""Type definitions for duck typing and schemas."""

from .protocols import (
    CommandValidatorProtocol,
    EnvironmentCleanerProtocol,
    InputDeviceEvDevProtocol,
    InputDevicePyDevProtocol,
    InputEventProtocol,
    KeyEventProtocol,
    ProcessRunnerProtocol,
)
from .schemas import (
    AppsModel,
    DeviceMappingsModel,
    IconsModel,
    MenuModel,
    WindowMode,
    WindowModel,
)

__all__ = [
    # Protocols - Device
    "InputEventProtocol",
    "KeyEventProtocol",
    "InputDeviceEvDevProtocol",
    "InputDevicePyDevProtocol",
    # Protocols - Command
    "CommandValidatorProtocol",
    "ProcessRunnerProtocol",
    "EnvironmentCleanerProtocol",
    # Schemas
    "AppsModel",
    "DeviceMappingsModel",
    "IconsModel",
    "MenuModel",
    "WindowModel",
    "WindowMode",
]
