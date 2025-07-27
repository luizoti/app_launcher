from PyQt5.QtWidgets import QMenu


class ContextMenu(QMenu):

    def __init__(self, parent=None, *args, **kwargs):
        super(ContextMenu, self).__init__(parent=parent, *args, **kwargs)
        self.change_visibility_action = self.addAction("Hide/Show")
        self.exit_action = self.addAction("Exit")
