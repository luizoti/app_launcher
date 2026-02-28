import typing

from PySide6.QtWidgets import QMenu, QWidget


class ContextMenu(QMenu):
        self.addSeparator()
        self.exit_action = self.addAction("Exit")
