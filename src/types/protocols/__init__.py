"""Protocols for type hints and duck typing."""

from .command import (
    CommandValidatorProtocol,
    EnvironmentCleanerProtocol,
    ProcessRunnerProtocol,
)
from .device import (
    InputDeviceEvDevProtocol,
    InputDevicePyDevProtocol,
    InputEventProtocol,
    KeyEventProtocol,
)

__all__ = [
    "InputEventProtocol",
    "KeyEventProtocol",
    "InputDeviceEvDevProtocol",
    "InputDevicePyDevProtocol",
    "CommandValidatorProtocol",
    "ProcessRunnerProtocol",
    "EnvironmentCleanerProtocol",
]
