from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout

from src.command_executor import CommandExecutor
from src.gui.centralized_resolution import CentralizedAppResolution
from src.gui.components.custom_button import CustomButton
from src.gui.components.grid import AppGrid
from src.gui.components.tray_icon import TrayIcon
from src.settings import SettingsManager
from src.utils import base64_to_icon


class AppMainWindow(QMainWindow):
    def __init__(self, settings=SettingsManager().get_settings()):
        super(AppMainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.settings = settings
        self.app_grid = AppGrid(row_limit=self.settings.get("window").get("apps_per_row"))

        self.setWindowTitle("Launcher de Aplicações")
        self.setFixedSize(
            self.settings.get("window").get("width"),
            self.settings.get("window").get("height"),
        )
        self._set_tray_icon()
        self._init_ui()
        print("INFO - Iniciando interface gráfica...")
        self._set_on_center()

    def _set_tray_icon(self):
        self.tray_icon = TrayIcon(parent=self)
        self.tray_icon.show()

    def _set_on_center(self):
        self.move(CentralizedAppResolution(app=self).centralized_resolution())

    def _from_config(self):
        # TODO: Get mappings from settings here
        pass

    def _get_apps_list(self):
        return self.settings.get("apps", {})

    def _launch_app(self, executor: CommandExecutor):
        executor.execute()
        self.hide()

    def _open_settings(self):
        # TODO: Open settings screen here
        print("⚙️ Configurações clicadas (implementar UI futura)")

    def _init_ui(self):
        central_widget = QWidget(self)
        main_layout = QVBoxLayout()
        created_app_grid = self.app_grid.render_app_grid(apps=self._get_apps_list())
        main_layout.addLayout(created_app_grid)
        main_layout.setAlignment(created_app_grid, Qt.AlignCenter)

        config_layout = QHBoxLayout()
        config_layout.addStretch()

        config_button = CustomButton()
        config_button.setIcon(base64_to_icon(self.settings.get("menu").get("settings")))
        config_button.setFixedSize(48, 48)
        config_button.setIconSize(QSize(40, 40))
        config_button.clicked.connect(self._open_settings)

        hide_button = CustomButton()
        hide_button.setIcon(base64_to_icon(self.settings.get("menu").get("hide")))
        hide_button.setFixedSize(48, 48)
        hide_button.setIconSize(QSize(40, 40))
        hide_button.clicked.connect(self.hide)
        config_layout.addWidget(hide_button)
        config_layout.addWidget(config_button)

        main_layout.addLayout(config_layout)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def switch_icon(self):
        # self.tray_icon.setIcon(base64_to_icon(connected=tray_icon_controller()))
        pass

    def hide(self):
        if self.isVisible():
            super(QMainWindow, self).hide()

    def show(self):
        if not self.isVisible():
            super(QMainWindow, self).show()

    def show_ui(self) -> None:
        if self.settings.get("window").get("fullscreen"):
            self.showFullScreen()
            return None
        self.show()
        return None
