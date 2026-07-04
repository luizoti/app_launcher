"""Protocols for device/input event handling (evdev, pyudev)."""

import typing
from collections.abc import Iterator


class InputEventProtocol(typing.Protocol):
    """Protocol for input events from evdev."""

    @property
    def type(self) -> int: ...
    @property
    def code(self) -> int: ...
    @property
    def value(self) -> int: ...

    keystate: int
    scancode: int


class KeyEventProtocol(InputEventProtocol):
    """Protocol for keyboard key events."""

    pass


class InputDeviceEvDevProtocol(typing.Protocol):
    """Protocol for evdev InputDevice."""

    @property
    def name(self) -> str: ...
    @property
    def path(self) -> str: ...

    def read_loop(self) -> Iterator[InputEventProtocol]: ...


class InputDevicePyDevProtocol(typing.Protocol):
    """Protocol for pyudev Device."""

    @property
    def device_node(self) -> str | None: ...
    @property
    def action(self) -> str | None: ...

    def get(self, key: str, default: typing.Any = None) -> typing.Any: ...
    def __getitem__(self, key: str) -> typing.Any: ...
