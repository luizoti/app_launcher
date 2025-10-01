from PyQt5.QtCore import QSize, Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QEnterEvent, QDragLeaveEvent
from PyQt5.QtWidgets import QPushButton

from src.utils import build_icon


class CustomButton(QPushButton):
    focused = pyqtSignal(str)

    def __init__(self, label: str = None, icon: str = None, on_click=None, name: str = None):
        self.name = name
        if not label:
            label = ""
        super(CustomButton, self).__init__(label)
        self.on_click = on_click

        self.default_color = "#FFFFFF"
        self.hover_color = "#444444"
        self.text_color = "#333333"

        self.setIconSize(QSize(100, 100))
        self.setMinimumSize(120, 120)
        self.setMaximumSize(120, 120)

        if icon:
            self.setIcon(build_icon(icon))

        self.setStyleSheet(self._get_stylesheet(background_color=self.default_color))

        self.clicked.connect(self._handle_click)

    def _handle_click(self):
        if self.on_click:
            self.on_click()

    def _get_stylesheet(self, background_color: str):
        return f"""
        QPushButton:focus {{
            background-color: gray;
            padding: none;
            outline: none;
        }}
        QPushButton {{
            font-size: 18px;
            background-color: {background_color};
            color: {self.text_color};
            border: 2px solid #555555;
            border-radius: 15px;
            padding: 10px;
            text-align: center;
        }}
        """

    def event(self, e):
        if e.type() == QEvent.KeyPress:
            self.focused.emit(self.name)
        return super(CustomButton, self).event(e)

    def enterEvent(self, event: QEnterEvent):
        self.setStyleSheet(self._get_stylesheet(self.hover_color))
        self.focused.emit(self.name)
        super().enterEvent(event)

    def leaveEvent(self, event: QDragLeaveEvent):
        self.setStyleSheet(self._get_stylesheet(self.default_color))
        super().leaveEvent(event)

    def keyPressEvent(self, event):
        self.click() if event.key() == Qt.Key_Return else super().keyPressEvent(event)
