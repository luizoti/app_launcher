import traceback
import typing

import more_itertools
from PyQt5.QtWidgets import QGridLayout

from src.command_executor import CommandExecutor
from src.gui.action_manager import ActionManager
from src.gui.components.custom_button import CustomButton


class AppGrid(QGridLayout, ActionManager):
    def __init__(self, row_limit: int = None):
        super(AppGrid, self).__init__()
        self.row_limit = row_limit

        self.mapped_grid = {}

        if not self.row_limit:
            raise AttributeError

    def __remove_from_grid(self, app_name=None):
        if not app_name:
            raise TypeError("Argument `app_name` cannot be null")
        index, app_widget = self.__search_app_on_grid(app_name=app_name)
        widget = app_widget.widget()
        if widget is not None:
            self.removeWidget(widget)
            widget.deleteLater()
        # self.__reorganize_grid()
        self.plot_app_grid()

    # def __reorganize_grid(self):
    #     widgets = []
    #     for i in reversed(range(self.count())):
    #         item = self.takeAt(i)
    #         widget = item.widget()
    #         if widget:
    #             widgets.append(widget)
    #     row = 0
    #     col = 0
    #     for widget in reversed(widgets):
    #         self.addWidget(widget, row, col)
    #         col += 1
    #         if col >= self.row_limit:
    #             col = 0
    #             row += 1

    def __search_app_on_grid(self, app_name):
        for index in range(0, 1000):
            button = self.itemAt(index)
            try:
                if button.widget().name == app_name:
                    return index, button
            except Exception as err:
                raise err
        return None

    @staticmethod
    def __button_generator(app_name, app_data):
        """Create a button with command based on app name and app data."""
        return CustomButton(
            icon_base64=app_data.get("icon"),
            on_click=CommandExecutor(command=app_data.get("cmd", [])).execute,
            name=app_name
        )

    def __rebuild_mapped_grid(self, apps: dict = None):
        if not apps:
            raise TypeError("Argument `apps` cannot be None")
        self.mapped_grid = dict(
            enumerate(more_itertools.batched([self.__button_generator(*x) for x in apps.items()], self.row_limit))
        )

    def enter(self):
        # TODO
        print("Enter pressed")

    def plot_app_grid(self, apps: dict = None):
        if not apps:
            raise TypeError("Argument `apps` cannot be None")
        self.__rebuild_mapped_grid(apps=apps)
        for row_index, apps in self.mapped_grid.items():
            for app_index, app in enumerate(apps):
                self.addWidget(app, row_index, app_index)
        return self

    def get_current_focus(self) -> typing.Tuple[int, int] | None:
        button: CustomButton
        for row_index, apps in self.mapped_grid.items():
            for app_index, button in enumerate(apps):
                if button.hasFocus():
                    return row_index, app_index
        return -1, -1

    def set_focus(self, row_index, app_index):
        try:
            list(self.mapped_grid.values())[row_index][app_index].setFocus()
        except IndexError:
            print("Index out of range {}, {}".format(row_index, app_index))
        except Exception:
            print(traceback.format_exc())

    def up(self):
        row_index, app_index = self.get_current_focus()
        if row_index == 0:
            if app_index > len(list(self.mapped_grid.values())[-1]) - 1 and len(self.mapped_grid.values()) > 2:
                self.set_focus(-2, app_index)
                return
            if app_index > len(list(self.mapped_grid.values())[-1]) - 1:
                print(app_index, len(list(self.mapped_grid.values())[-1]) - 1)
                self.set_focus(-1, len(list(self.mapped_grid.values())[-1]) - 1)
                return

            if app_index >= len(list(self.mapped_grid.values())[-1]) - 1:
                self.set_focus(-1, app_index)
                return
            else:
                self.set_focus(-1, app_index)
                return
        self.set_focus(row_index - 1, app_index)
        return

    def down(self):
        row_index, app_index = self.get_current_focus()

        if app_index > len(list(self.mapped_grid.values())[-1]) - 1 and row_index >= 1:
            self.set_focus(0, app_index)
            return
        if app_index > len(list(self.mapped_grid.values())[-1]) - 1:
            self.set_focus(row_index + 1, app_index)
            return
        if row_index == len(self.mapped_grid) - 1:
            self.set_focus(0, app_index)
            return

        self.set_focus(row_index + 1, app_index)
        return

    def left(self):
        row_index, app_index = self.get_current_focus()
        if app_index == 0:
            self.set_focus(row_index - 1, len(list(self.mapped_grid.values())[row_index - 1]) - 1)
            return
        self.set_focus(row_index, app_index - 1)
        return

    def right(self):
        row_index, app_index = self.get_current_focus()

        if row_index == len(self.mapped_grid) - 1 and app_index == len(list(self.mapped_grid.values())[row_index]) - 1:
            self.set_focus(0, 0)
            return
        if app_index == self.row_limit - 1:
            self.set_focus(row_index + 1, 0)
            return

        self.set_focus(row_index, app_index + 1)
        return
