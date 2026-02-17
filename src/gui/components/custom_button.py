import typing

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsColorizeEffect, QPushButton

from src.utils import build_icon

ICO_PADDING = 16


class CustomButton(QPushButton):
    focused = Signal(str)

    def __init__(
        self,
        label: typing.Optional[str] = None,
        icon: typing.Optional[str] = None,
        on_click: typing.Optional[typing.Callable[[typing.Union[list[str], str]], None]] = None,
        name: typing.Optional[str] = None,
        size: typing.Optional[tuple[int,...]]=None,
        icon_size: typing.Optional[QSize] = None,
    ):
        self.name = name or ""
        self.disable_animation = False
        super(CustomButton, self).__init__(label if label else "")
        self.on_click = on_click
        self.normal_color = "#FFFFFF"
        self.hover_color = "#444444"
        self.text_color = "#333333"
        self.normal_size = size[0] - ICO_PADDING if size else 112
        self.focused_size = icon_size.width() + ICO_PADDING if icon_size is not None else 128
        self.setStyleSheet(self._get_stylesheet(self.normal_color))
        self.setFixedSize(
            *(
                self.normal_size,
                self.normal_size,
            )
        )
        self.setIconSize(QSize(self.focused_size, self.focused_size))
        self.setIcon(build_icon(icon))
        self.effect = QGraphicsColorizeEffect(self)
        self.effect.setColor(QColor(0, 0, 0))
        self.effect.setStrength(0.8)
        self.setGraphicsEffect(self.effect)
        self.clicked.connect(self._handle_click)
        self._update_visuals(False)

    def _get_stylesheet(self, background_color: str):
        return f"""
        QPushButton {{
            font-size: 18px;
            background-color: {background_color};
            color: {self.text_color if background_color == self.normal_color else self.normal_color};
            border: 0px solid #555555;
            border-radius: 10px;
            text-align: center;
        }}
        QPushButton:focus {{
            outline: none;
        }}
        """

    def no_animation(self):
        self.disable_animation = True

    def _update_visuals(self, is_active: bool):
        ico_sizes = (
            (self.focused_size, self.focused_size)
            if is_active
            else (self.normal_size, self.normal_size)
        )
        self.effect.setEnabled(not is_active)
        self.setStyleSheet(
            self._get_stylesheet(self.normal_color if is_active else self.hover_color)
        )
        if self.disable_animation:
            return None
        self.set_ico_size(*ico_sizes)
        self.setMaximumSize(*ico_sizes)
        if is_active:
            self.focused.emit(self.name)

    def set_ico_size(self, width: int, height: int):
        self.setIconSize(QSize(width, height))

    def _handle_click(self) -> None:
        if self.on_click:
            self.on_click()

    def enterEvent(self, event) -> None:
        self._update_visuals(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._update_visuals(self.hasFocus())
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self._update_visuals(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._update_visuals(self.underMouse())
        super().focusOutEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.click()
        else:
            super().keyPressEvent(event)
