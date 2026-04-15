import logging

from PySide6.QtCore import QObject, QSize, Qt
from PySide6.QtGui import QColor, QFont, QKeyEvent, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from src.gui.action_manager import ActionManager
from src.gui.centralized_resolution import CentralizedAppResolution
from src.gui.components.custom_button import CustomButton
from src.gui.components.device_monitor import DeviceMonitor
from src.gui.components.grid import AppGrid
from src.gui.components.tray_icon import TrayIcon
from src.gui.icons.cache_loader import get_icon
from src.instance import destroy_pid_file
from src.settings import Settings, get_settings
from src.types.schemas import AppsModel, WindowMode

logger: logging.Logger = logging.getLogger(__name__)
settings: Settings = get_settings()


class KeyPressFilter(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress:
            self.window.keyPressEvent(event)
            return True
        return False


class AppMainWindow(QMainWindow, ActionManager):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(get_icon(settings.tray.standby))
        self._apply_window_mode(settings.window.window_mode)
        self.app_grid = AppGrid(row_limit=settings.window.apps_per_row)
        self.info_label = QLabel("Select an app")
        self.info_label.setFont(QFont("Arial", 12, weight=QFont.Weight.Bold))

        self.setWindowTitle("Application Launcher")
        self.setFixedSize(
            settings.window.width,
            settings.window.height,
        )

        self.tray_icon = TrayIcon(parent=self)
        self.device_monitor_worker = DeviceMonitor()

        self._init_ui()
        logger.info("Starting AppLauncher interface")
        self._set_on_center()
        self.tray_icon.show()

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#202326"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self._set_signals()
        self.device_monitor_worker.start_monitor()

        self.key_filter = KeyPressFilter(self)
        QApplication.instance().installEventFilter(self.key_filter)

    def _set_signals(self):
        self.tray_icon.tray_action.connect(self.action_handler)

        self.device_monitor_worker.tray_action.connect(
            self.tray_icon.handler_switch_icon
        )

        self.device_monitor_worker.connection_status.connect(
            self.tray_icon.handle_connection_status
        )

        self.device_monitor_worker.action.connect(self.app_grid.action_handler)
        self.device_monitor_worker.action.connect(self.action_handler)

    def _set_on_center(self):
        self.move(CentralizedAppResolution(app=self).centralized_resolution())

    def _get_apps_list(self) -> dict[str, AppsModel]:
        return settings.apps

    def _open_settings(self):
        logger.debug("Settings clicked (implement future UI)")

    def _change_label_text(self, new_text: str) -> None:
        self.info_label.setText(new_text.capitalize())

    def _init_ui(self):
        central_widget = QWidget(self)
        main_layout = QVBoxLayout()

        created_app_grid: QGridLayout = self.app_grid.plot_app_grid(
            apps=self._get_apps_list(),
            label_changer=self._change_label_text,
            hide_window=self.hide,
        )

        main_layout.addLayout(created_app_grid)
        main_layout.setAlignment(created_app_grid, Qt.AlignmentFlag.AlignCenter)

        config_layout = QHBoxLayout()

        config_button = CustomButton(
            name="Settings", size=(48, 48), icon_size=QSize(40, 40)
        )
        config_button.no_animation()
        config_button.focused_change_label.connect(self._change_label_text)
        config_button.setIcon(get_icon(settings.menu.settings))
        config_button.clicked.connect(self._open_settings)

        hide_button = CustomButton(name="Hide", size=(48, 48), icon_size=QSize(40, 40))
        hide_button.no_animation()
        hide_button.setIcon(get_icon(settings.menu.hide))
        hide_button.clicked.connect(self.hide)

        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        config_layout.addWidget(self.info_label)
        config_layout.addWidget(hide_button)
        config_layout.addWidget(config_button)

        main_layout.addLayout(config_layout)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def show_ui(self) -> None:
        self.setVisible(True)
        return None

    def toggle_view(self):
        if self.isVisible():
            self.setVisible(False)
            return None
        self.setVisible(True)
        return None

    def action_handler(self, action_name: str) -> None:
        logger.debug(f"action_handler called: {action_name}")
        if action_name == "toggle_view":
            self.toggle_view()
            return

        if not self.isVisible():
            logger.debug(f"action_handler: app not visible, ignoring {action_name}")
            return

        method = getattr(self, action_name, None)
        if callable(method):
            method()

    def _apply_window_mode(self, mode: WindowMode | None = None) -> None:
        mode = mode or settings.window.window_mode

        if mode == WindowMode.BORDERLESS:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
            )
            self.setFixedSize(settings.window.width, settings.window.height)
        elif mode == WindowMode.MAXIMIZED:
            self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
            self.showMaximized()
        elif mode == WindowMode.FULLSCREEN:
            self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
            self.showFullScreen()

        self.show()

    def _cycle_window_mode(self) -> None:
        if not self.isVisible():
            return

        modes = list(WindowMode)
        current = modes.index(settings.window.window_mode)
        next_mode = modes[(current + 1) % len(modes)]
        settings.window.window_mode = next_mode
        self._apply_window_mode(next_mode)
        logger.info(f"Window mode changed to: {next_mode.value}")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Tab:
            self._cycle_window_mode()
        else:
            super().keyPressEvent(event)

    def __exit__(self):
        destroy_pid_file()
