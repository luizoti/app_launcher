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

    def _is_app_visible(self) -> bool:
        parent_widget: QWidget = self.parentWidget()
        if parent_widget:
            sub_parent_widget: QWidget | None = parent_widget.parentWidget()
            if sub_parent_widget:
                return sub_parent_widget.isVisible()
        return False

    def enter(self) -> None:
        """
        Emit clicked signal from CustomButton to opem app and hide AppMainWindow
        based on app row and app columns.
        """
        if not self._is_app_visible():
            return

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
            LOGGER.debug(
                f"IndexError on __set_focus - invalid pos ({row_index}, {app_index})"
            )
        except Exception:
            LOGGER.exception(
                f"Error on __set_focus(row_index={row_index}, app_index={app_index})"
            )

    def _get_grid_size(self) -> tuple[int, int]:
        if not self.mapped_grid:
            return (0, 0)
        num_rows = len(self.mapped_grid)
        num_cols = len(self.mapped_grid[0]) if self.mapped_grid else 0
        return (num_rows, num_cols)

    def _is_valid_position(self, row_index: int, app_index: int) -> bool:
        try:
            self.mapped_grid[row_index][app_index]
            return True
        except IndexError:
            return False

    def _normalize_position(self) -> None:
        num_rows, num_cols = self._get_grid_size()
        if num_rows == 0 or num_cols == 0:
            return

        # Calcular novas posições com overflow
        if self.current_app >= num_cols:
            self.current_row += self.current_app // num_cols
            self.current_app = self.current_app % num_cols
        elif self.current_app < 0:
            # LEFT no primeiro item → último item da última linha
            self.current_row = num_rows - 1
            self.current_app = num_cols - 1

        # Normalizar row
        self.current_row = self.current_row % num_rows

        # Validar posição
        if not self._is_valid_position(self.current_row, self.current_app):
            self.current_row = 0
            self.current_app = 0

    def up(self) -> None:
        if not self._is_app_visible():
            return
        self.current_row -= 1
        self._normalize_position()
        self.__set_focus(self.current_row, self.current_app)

    def down(self) -> None:
        if not self._is_app_visible():
            return
        self.current_row += 1
        self._normalize_position()
        self.__set_focus(self.current_row, self.current_app)

    def left(self) -> None:
        if not self._is_app_visible():
            return
        self.current_app -= 1
        self._normalize_position()
        self.__set_focus(self.current_row, self.current_app)

    def right(self) -> None:
        if not self._is_app_visible():
            return
        self.current_app += 1
        self._normalize_position()
        self.__set_focus(self.current_row, self.current_app)
