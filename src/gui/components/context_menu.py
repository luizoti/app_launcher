from PyQt5.QtWidgets import QMenu


class ContextMenu(QMenu):

    def __init__(self, parent=None, *args, **kwargs):
        super(ContextMenu, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.change_visibility_action = self.addAction("Hide/Show")
        self.change_visibility_action.triggered.connect(self._change_visibility_handler)

        self.exit_action = self.addAction("Exit")
        self.exit_action.triggered.connect(self.parent.close)

    def _change_visibility_handler(self):
        self.parent.hide() if self.parent.isVisible() else self.parent.show()
