import logging
import typing

import more_itertools
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QGridLayout, QWidget

from src import command_executor
from src.gui.action_manager import ActionManager
from src.gui.components.custom_button import CustomButton
from src.settings_model import AppsModel

LOGGER: logging.Logger = logging.getLogger(__name__)


class AppGrid(QGridLayout, ActionManager):
    actions = Signal(int)

    def __init__(self, row_limit: int = 6):
        super().__init__()
        self.row_limit: int = row_limit
        self.mapped_grid: list[tuple[CustomButton, ...]] = []
        self._last_position: tuple[int, ...] = (0, 0)
        self.current_row: int = 0
        self.current_app: int = 0

    @staticmethod
    def __button_generator(
        app_name: str,
        app_data: AppsModel,
        label_changer: typing.Callable[[str], None],
    ) -> CustomButton:
        """Create a button with command based on app name and app data."""
        return CustomButton(
            icon=app_data.icon,
            on_click=lambda _: command_executor.command_executor(
                command=app_data.cmd, label_changer=label_changer
            ),
            name=app_name,
        )

    def __rebuild_mapped_grid(
        self,
        apps: dict[str, AppsModel],
        label_changer: typing.Callable[[str], None],
    ) -> None:
        """Rebuild mapped grid dictionary based on settings app list."""
        apps_iter: typing.Generator[CustomButton] = (
            self.__button_generator(*x, label_changer=label_changer)
            for x in apps.items()
        )
        self.mapped_grid: list[tuple[CustomButton, ...]] = list(
            more_itertools.batched(
                iterable=apps_iter,
                n=self.row_limit,
            )
        )
        del apps_iter

    def enter(self) -> None:
        """
        Emit clicked signal from CustomButton to opem app and hide AppMainWindow
        based on app row and app columns.
        """
        self.mapped_grid[self.current_row][self.current_app].clicked.emit()
        parent_widget: QWidget = self.parentWidget()
        if parent_widget:
            sub_parent_widget: QWidget | None = parent_widget.parentWidget()
            if sub_parent_widget:
                sub_parent_widget.hide()

    @Slot()
    def _change_focus_on_hover(self) -> None:
        self.__set_focus(row_index=self.current_row, app_index=self.current_app)

    def plot_app_grid(
        self,
        apps: dict[str, AppsModel],
        label_changer: typing.Callable[[str], None],
    ) -> "AppGrid":
        """Feed GridWidgets based on a list of apps."""
        self.__rebuild_mapped_grid(apps=apps, label_changer=label_changer)
        for row_index, apps_tuple in enumerate(iterable=self.mapped_grid):
            for app_index, app in enumerate(iterable=apps_tuple):
                app.focused_change_label.connect(label_changer)
                app.change_focus_on_hover.connect(self._change_focus_on_hover)
                self.addWidget(
                    app, row_index, app_index, alignment=Qt.AlignmentFlag.AlignCenter
                )
        return self

    def __set_focus(self, row_index: int, app_index: int) -> None:
        try:
            self.mapped_grid[row_index][app_index].setFocus()
            self._last_position = (self.current_row, self.current_app)
        except IndexError:
            self.__set_focus(*self._last_position)
            LOGGER.debug("IndexError on __set_focus - fallback to last position")
        except Exception:
            LOGGER.exception(
                f"Error on __set_focus(row_index={row_index}, app_index={app_index})"
            )

    def up(self) -> None:
        LOGGER.debug("up")
        if self.current_row > 0:
            self.current_row -= 1
        else:
            self.current_row += 1
        self.__set_focus(self.current_row, self.current_app)

    def down(self) -> None:
        LOGGER.debug("down")
        if self.current_row > 0:
            self.current_row -= 1
        else:
            self.current_row += 1
        self.__set_focus(self.current_row, self.current_app)

    def left(self) -> None:
        LOGGER.debug("left")
        if self.current_app > 0:
            self.current_app -= 1
        else:
            self.current_app = self.row_limit - 1
            self.current_row += 1
        self.__set_focus(self.current_row, self.current_app)

    def right(self) -> None:
        LOGGER.debug("right")
        self.current_app += 1
        self.__set_focus(self.current_row, self.current_app)
