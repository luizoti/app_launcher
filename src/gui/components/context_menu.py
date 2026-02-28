import typing

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMenu, QWidget


class ContextMenu(QMenu):
        self.addSeparator()
        self.exit_action = self.addAction("Exit")
        q_app_instance = QCoreApplication.instance()
        if q_app_instance:
            self.exit_action.triggered.connect(q_app_instance.quit)
