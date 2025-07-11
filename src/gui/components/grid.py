from PyQt5.QtWidgets import QGridLayout

from src.gui.app import CommandExecutor
from src.gui.components.custom_button import CustomButton


class AppGrid(QGridLayout):
    def __init__(self, row_limit: int = None):
        super(AppGrid, self).__init__()
        self.row_limit = row_limit
        if not self.row_limit:
            print("ERRO - No row limit")
            raise AttributeError

    def remove_from_grid(self, app_name=None):
        if not app_name:
            raise TypeError("app_name cannot be null")
        index, app_widget = self.__search_app_on_grid(app_name=app_name)
        widget = app_widget.widget()
        if widget is not None:
            self.removeWidget(widget)
            widget.deleteLater()
        self._reorganize_grid()

    def _reorganize_grid(self):
        widgets = []
        for i in reversed(range(self.count())):
            item = self.takeAt(i)
            widget = item.widget()
            if widget:
                widgets.append(widget)
        row = 0
        col = 0
        for widget in reversed(widgets):
            self.addWidget(widget, row, col)
            col += 1
            if col >= self.row_limit:
                col = 0
                row += 1

    def __search_app_on_grid(self, app_name):
        for index in range(0, 1000):
            button = self.itemAt(index)
            try:
                if button.widget().name == app_name:
                    return index, button
            except Exception as err:
                raise err
        return None

    def render_app_grid(self, apps: dict = None):
        if not apps:
            print("No apps from argument - apps")
        row = 0
        row_app_counter = 0

        for app_name, app_settings in apps.items():
            if row_app_counter == self.row_limit:
                row += 1
                row_app_counter = 0
            executor = CommandExecutor(command=app_settings.get("cmd", []))
            button = CustomButton(
                icon_base64=app_settings.get("icon"),
                on_click=executor.execute,
                name=app_name
            )
            self.addWidget(button, row, row_app_counter)
            row_app_counter += 1
        return self
