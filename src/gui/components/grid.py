import traceback
import typing
from typing import Dict, Text

import more_itertools
from PyQt5.QtCore import pyqtSlot  # type: ignore
from PyQt5.QtWidgets import QGridLayout

from src.command_executor import CommandExecutor
from src.gui.action_manager import ActionManager
from src.gui.components.custom_button import CustomButton
from src.settings_model import AppsModel


class AppGrid(QGridLayout, ActionManager):

    def __init__(self, row_limit: int = 6):
        super(AppGrid, self).__init__()
        self.row_limit = row_limit
        # TODO: Now, this is a predefined fixed app row; the tuple represents this fixed size.
        # In the future, if it is possible to add new apps, this can be changed to a list.
        self.mapped_grid: dict[int, tuple[CustomButton, ...]] = {}

        if not self.row_limit:
            raise AttributeError

    # def __remove_from_grid(self, app_name=None):
    #     # TODO: This cam be changed, maybe search on self.mapped_grid
    #     if not app_name:
    #         raise TypeError("Argument `app_name` cannot be null")
    #     index, app_widget = self.__search_app_on_grid(app_name=app_name)
    #     widget = app_widget.widget()
    #     if widget is not None:
    #         self.removeWidget(widget)
    #         widget.deleteLater()
    #     # self.__reorganize_grid()
    #     self.plot_app_grid()

    # TODO: __rebuild_mapped_grid probably replace this
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

    # def __search_app_on_grid(self, app_name):
    #     for app_index in range(len(self.mapped_grid)):
    #         button = self.itemAt(app_index)
    #         print("button", button)
    #         try:
    #             widget:QWidget = button.widget()
    #             if not widget:
    #                 raise Exception("Widget of button cannot be None")
    #             if widget.name == app_name:
    #                 return app_index, button
    #         except Exception as err:
    #             raise err
    #     return None

    @staticmethod
    def __button_generator(app_name: typing.Text, app_data:AppsModel, label_changer: typing.Optional[typing.Callable[[typing.Text], None]]=None):
        if not label_changer:
            raise TypeError("Argument `label_changer` cannot be null")
        """Create a button with command based on app name and app data."""
        return CustomButton(
            icon=app_data.icon,
            on_click=CommandExecutor(
                command=app_data.cmd, 
                label_changer=label_changer
            ).execute,
            name=app_name,
        )

    def __rebuild_mapped_grid(self, apps: Dict[Text, AppsModel], label_changer: typing.Optional[typing.Callable[[typing.Text], None]]=None) -> None:
        """Rebuild mapped grid dictionary based on settings app list."""
        if not apps:
            raise TypeError("Argument `apps` cannot be None")
        apps_iter: typing.Generator[CustomButton] = (self.__button_generator(*x, label_changer=label_changer) for x in apps.items())
        self.mapped_grid = dict(enumerate(
                more_itertools.batched(
                    apps_iter,
                    self.row_limit,
                )
            ))

    def enter(self):
        """Emit clicked signal from CustomButton to opem app and hide AppMainWindow based on app row and app columns."""
        row_index, app_index = self.__get_current_focus()
        pressed_button: CustomButton = self.mapped_grid[row_index][app_index]
        pressed_button.clicked.emit()
        parent_widget = self.parentWidget()
        if parent_widget:
            sub_parent_widget = parent_widget.parentWidget()
            if sub_parent_widget:
                sub_parent_widget.hide()

    @pyqtSlot(str)
    def _change_focus_on_hover(self, focused_app: typing.Text) -> None:
        for row_index, apps in self.mapped_grid.items():
            for app_index, app in enumerate(apps):
                if focused_app == app.name:
                    self.__set_focus(row_index, app_index)

    def plot_app_grid(self, apps: Dict[Text, AppsModel], label_changer:typing.Optional[typing.Callable[[typing.Text], None]]=None) -> typing.Self:
        """Feed GridWidgets based on a list of apps."""
        if not apps:
            raise TypeError("Argument `apps` cannot be None")
        self.__rebuild_mapped_grid(apps=apps, label_changer=label_changer)
        for row_index, apps_tuple in self.mapped_grid.items():
            for app_index, app in enumerate(apps_tuple):
                if label_changer:
                    app.focused.connect(label_changer)
                app.focused.connect(self._change_focus_on_hover)
                self.addWidget(app, row_index, app_index)
        return self

    def __get_current_focus(self) -> tuple[int, int]:
        for row_index, apps in self.mapped_grid.items():
            for app_index, button in enumerate(apps):
                if button.hasFocus():
                    return row_index, app_index
        return -1, -1

    def __set_focus(self, row_index: int, app_index: int) -> None:
        try:
            list(self.mapped_grid.values())[row_index][app_index].setFocus()
        except IndexError:
            print("Index out of range {}, {}".format(row_index, app_index))
        except Exception:
            print(traceback.format_exc())

    def up(self):
        row_index, app_index = self.__get_current_focus()
        if row_index == 0:
            if (
                app_index > len(list(self.mapped_grid.values())[-1]) - 1
                and len(self.mapped_grid.values()) > 2
            ):
                self.__set_focus(-2, app_index)
                return
            if app_index > len(list(self.mapped_grid.values())[-1]) - 1:
                print(app_index, len(list(self.mapped_grid.values())[-1]) - 1)
                self.__set_focus(-1, len(list(self.mapped_grid.values())[-1]) - 1)
                return
            if app_index >= len(list(self.mapped_grid.values())[-1]) - 1:
                self.__set_focus(-1, app_index)
                return
            else:
                self.__set_focus(-1, app_index)
                return
        self.__set_focus(row_index - 1, app_index)
        return

    def down(self):
        row_index, app_index = self.__get_current_focus()
        if app_index > len(list(self.mapped_grid.values())[-1]) - 1 and row_index >= 1:
            self.__set_focus(0, app_index)
            return
        if app_index > len(list(self.mapped_grid.values())[-1]) - 1:
            self.__set_focus(row_index + 1, app_index)
            return
        if row_index == len(self.mapped_grid) - 1:
            self.__set_focus(0, app_index)
            return
        self.__set_focus(row_index + 1, app_index)
        return

    def left(self):
        row_index, app_index = self.__get_current_focus()
        if app_index == 0:
            self.__set_focus(
                row_index - 1, len(list(self.mapped_grid.values())[row_index - 1]) - 1
            )
            return
        self.__set_focus(row_index, app_index - 1)
        return

    def right(self):
        row_index, app_index = self.__get_current_focus()
        if (
            row_index == len(self.mapped_grid) - 1
            and app_index == len(list(self.mapped_grid.values())[row_index]) - 1
        ):
            self.__set_focus(0, 0)
            return
        if app_index == self.row_limit - 1:
            self.__set_focus(row_index + 1, 0)
            return
        self.__set_focus(row_index, app_index + 1)
        return
