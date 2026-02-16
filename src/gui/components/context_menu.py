import typing

from PyQt5.QtWidgets import QMenu, QWidget


class ContextMenu(QMenu):

    def __init__(self, parent: typing.Optional[QWidget]=None, *args: typing.Any, **kwargs: typing.Any):
        super(ContextMenu, self).__init__(parent=parent, *args, **kwargs)
        self.change_visibility_action = self.addAction("Hide/Show") # type: ignore
        self.exit_action = self.addAction("Exit") # type: ignore
