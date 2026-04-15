"""Protocols for device/input event handling (evdev, pyudev)."""

import typing


class InputEventProtocol(typing.Protocol):
    """Protocol for input events from evdev."""

    @property
    def type(self) -> int: ...
    @property
    def code(self) -> int: ...
    @property
    def value(self) -> int: ...

    keystate: str
    scancode: str


class KeyEventProtocol(InputEventProtocol):
    """Protocol for keyboard key events."""

    pass


class InputDeviceEvDevProtocol(typing.Protocol):
    """Protocol for evdev InputDevice."""

    @property
    def name(self) -> str: ...
    @property
    def path(self) -> str: ...

    def read_loop(self): ...  # type: ignore


class InputDevicePyDevProtocol(typing.Protocol):
    """Protocol for pyudev Device."""

    @property
    def device_node(self) -> str | None: ...
    @property
    def action(self) -> str | None: ...

    def get(self, key: str, default: typing.Any = None) -> typing.Any: ...
    def __getitem__(self, key: str) -> typing.Any: ...
