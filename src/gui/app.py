from PyQt5.QtCore import Qt, QSize, QThread
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QLabel, QWidget
from src.gui.action_manager import ActionManager
from src.gui.centralized_resolution import CentralizedAppResolution
from src.gui.components.custom_button import CustomButton
from src.gui.components.device_monitor import DeviceMonitor
from src.gui.components.grid import AppGrid
from src.gui.components.tray_icon import TrayIcon
from src.insancie import destroy_pid_file
from src.settings import SettingsManager
from src.utils import build_icon


class AppMainWindow(QMainWindow, ActionManager):
    def __init__(self, settings=SettingsManager().get_settings()):
        super(AppMainWindow, self).__init__()
        self.setWindowIcon(build_icon(settings.get("tray").get("icons").get("standby")))
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.FramelessWindowHint) | Qt.WindowFlags(Qt.WindowType.WindowStaysOnTopHint))
        self.settings = settings
        self.app_grid = AppGrid(row_limit=self.settings.get("window").get("apps_per_row"))
        self.info_label = QLabel("Selecione um app")
        self.info_label.setFont(QFont("Arial", 12, weight=QFont.Weight.Bold))
        self.setWindowTitle("Launcher de Aplicações")
        self.setFixedSize(
            self.settings.get("window").get("width"),
            self.settings.get("window").get("height"),
        )
        self.tray_icon = TrayIcon(parent=self)
        self._thread = self.thread()

        self.device_monitor_worker = DeviceMonitor()
        self.device_monitor_worker.moveToThread(self._thread)
        self._set_signals()
        self._init_ui()
        print("INFO - Iniciando interface gráfica...")
        self._set_on_center()
        self.tray_icon.show()

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#202326"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        if not self._thread:
            raise RuntimeError("Cannot start, problem to start thread.")
        self._thread.start()

    def _set_signals(self):
        self.device_monitor_worker.action.connect(self.action_handler)

        self.tray_icon.tray_action.connect(self.action_handler)
        self.device_monitor_worker.action.connect(self.app_grid.action_handler)
        if not self._thread:
            raise RuntimeError("Cannot connect signals, problem to start thread.")
        self._thread.started.connect(self.device_monitor_worker.start_monitor)
        self._thread.finished.connect(self._thread.deleteLater)

    def _set_on_center(self):
        self.move(CentralizedAppResolution(app=self).centralized_resolution())

    def _get_apps_list(self):
        return self.settings.get("apps", {})

    def _open_settings(self):
        # TODO: Open settings screen here
        print("⚙️ Configurações clicadas (implementar UI futura)")

    def _change_label_text(self, new_text: str):
        self.info_label.setText(new_text.capitalize())

    def _init_ui(self):
        central_widget = QWidget(self)
        main_layout = QVBoxLayout()
        created_app_grid = self.app_grid.plot_app_grid(
            apps=self._get_apps_list(),
            label_changer=self._change_label_text
        )
        main_layout.addLayout(created_app_grid)
        main_layout.setAlignment(created_app_grid, Qt.AlignmentFlag.AlignCenter)

        config_layout = QHBoxLayout()

        config_button = CustomButton(name="Configuração", size=(48, 48), icon_size=QSize(40, 40))
        config_button.no_animation()
        config_button.focused.connect(self._change_label_text)
        config_button.setIcon(build_icon(self.settings.get("menu").get("settings")))
        config_button.clicked.connect(self._open_settings)
        config_button.focused.connect(self._change_label_text)

        hide_button = CustomButton(name="Esconder", size=(48, 48), icon_size=QSize(40, 40))
        hide_button.no_animation()

        hide_button.setIcon(build_icon(self.settings.get("menu").get("hide")))
        hide_button.clicked.connect(self.hide)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        config_layout.addWidget(self.info_label)
        config_layout.addWidget(hide_button)
        config_layout.addWidget(config_button)

        main_layout.addLayout(config_layout)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def show_ui(self) -> None:
        if self.settings.get("window").get("fullscreen"):
            self.showFullScreen()
            return None
        self.show()
        return None

    def toggle_view(self):
        if self.isVisible():
            self.hide()
            return None
        self.show()
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        destroy_pid_file()
