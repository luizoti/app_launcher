import typing

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtGui import QColor, QEnterEvent, QFocusEvent, QKeyEvent
from PySide6.QtWidgets import QGraphicsColorizeEffect, QPushButton

from src.gui.icons.cache_loader import get_icon

ICO_PADDING = 16


class CustomButton(QPushButton):
    focused_change_label = Signal(str)
    change_focus_on_hover = Signal()

    def __init__(
        self,
        label: str | None = None,
        icon: str | None = None,
        on_click: typing.Callable[[list[str] | str], None] | None = None,
        name: str | None = None,
        size: tuple[int, ...] | None = None,
        icon_size: QSize | None = None,
    ):
        self.name = name or ""
        self.disable_animation = False
        super().__init__(label if label else "")
        self.normal_color = "#FFFFFF"
        self.hover_color = "#444444"
        self.text_color = "#333333"
        self.normal_size: int = size[0] - ICO_PADDING if size else 112
        self.focused_size: int = (
            icon_size.width() + ICO_PADDING if icon_size is not None else 128
        )
        self.setStyleSheet(self._get_stylesheet(self.normal_color))
        self.setFixedSize(
            *(
                self.normal_size,
                self.normal_size,
            )
        )
        self.setIconSize(QSize(self.focused_size, self.focused_size))
        self.setIcon(get_icon(icon))
        self.effect = QGraphicsColorizeEffect(self)
        self.effect.setColor(QColor(0, 0, 0))
        self.effect.setStrength(0.8)
        self.setGraphicsEffect(self.effect)
        if on_click:
            self.clicked.connect(on_click)
        self._update_visuals(False)

    def _get_stylesheet(self, background_color: str) -> str:
        return f"""
        QPushButton {{
            font-size: 18px;
            background-color: {background_color};
            color: {
            self.text_color
            if background_color == self.normal_color
            else self.normal_color
        };
            border: 0px solid #555555;
            border-radius: 10px;
            text-align: center;
        }}
        QPushButton:focus {{
            outline: none;
        }}
        """

    def no_animation(self) -> None:
        self.disable_animation = True

    def _update_visuals(self, is_active: bool) -> None:
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
            return
        self.set_ico_size(*ico_sizes)
        self.setMaximumSize(*ico_sizes)
        if is_active:
            self.focused_change_label.emit(self.name)

    def set_ico_size(self, width: int, height: int) -> None:
        self.setIconSize(QSize(width, height))

    def enterEvent(self, event: QEnterEvent) -> None:
        self._update_visuals(True)
        super().enterEvent(event)
        self.change_focus_on_hover.emit()

    def leaveEvent(self, event: QEvent) -> None:
        self._update_visuals(self.hasFocus())
        super().leaveEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:
        self._update_visuals(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self._update_visuals(self.underMouse())
        super().focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.click()
        else:
            super().keyPressEvent(event)
