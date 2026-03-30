import typing

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMenu, QWidget


class ContextMenu(QMenu):
    def __init__(
        self,
        parent: QWidget | None = None,
        *args: typing.Any,
        **kwargs: typing.Any,
    ):
        super().__init__(*args, **kwargs, parent=parent)
        self.change_visibility_action = self.addAction("Hide/Show")
        self.addSeparator()
        self.exit_action = self.addAction("Exit")
        q_app_instance = QCoreApplication.instance()
        if q_app_instance:
            self.exit_action.triggered.connect(q_app_instance.quit)
