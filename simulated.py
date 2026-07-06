import sys
from datetime import datetime

from evdev import UInput
from evdev import ecodes as e
from evdev.device import AbsInfo
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Mapeamento código evdev → ação no app_launcher
ACTION_MAP: dict[int, str] = {
    e.BTN_A: "enter",
    e.BTN_MODE: "toggle_view",
}

DPAD_ABS_MAP: dict[int, dict[int, str]] = {
    e.ABS_HAT0X: {-1: "left", 1: "right"},
    e.ABS_HAT0Y: {-1: "up", 1: "down"},
}


class DualGamepad(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Universal Virtual Controller (Xbox & PS)")
        self.setMinimumWidth(850)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.button_map: dict[int, QPushButton] = {}

        self.ui = UInput(
            {
                e.EV_KEY: [
                    e.BTN_A,
                    e.BTN_B,
                    e.BTN_X,
                    e.BTN_Y,
                    e.BTN_TL,
                    e.BTN_TR,
                    e.BTN_TL2,
                    e.BTN_TR2,
                    e.BTN_SELECT,
                    e.BTN_START,
                    e.BTN_MODE,
                ],
                e.EV_ABS: [
                    (e.ABS_HAT0X, AbsInfo(0, -1, 1, 0, 0, 0)),
                    (e.ABS_HAT0Y, AbsInfo(0, -1, 1, 0, 0, 0)),
                ],
            },
            name="Virtual Joystick",
        )

        self.button_configs = [
            ("LT", "L2", e.BTN_TL2),
            ("RT", "R2", e.BTN_TR2),
            ("LB", "L1", e.BTN_TL),
            ("RB", "R1", e.BTN_TR),
            ("Y", "△", e.BTN_Y),
            ("B", "○", e.BTN_B),
            ("A", "✕", e.BTN_A),
            ("X", "□", e.BTN_X),
            ("Back", "Share", e.BTN_SELECT),
            ("Start", "Options", e.BTN_START),
            ("Guide", "PS", e.BTN_MODE),
        ]

        self.keyboard_map = {
            Qt.Key_Up: (e.EV_ABS, e.ABS_HAT0Y, -1),
            Qt.Key_Down: (e.EV_ABS, e.ABS_HAT0Y, 1),
            Qt.Key_Left: (e.EV_ABS, e.ABS_HAT0X, -1),
            Qt.Key_Right: (e.EV_ABS, e.ABS_HAT0X, 1),
            Qt.Key_Z: (e.EV_KEY, e.BTN_A, 1),
            Qt.Key_X: (e.EV_KEY, e.BTN_B, 1),
            Qt.Key_Space: (e.EV_KEY, e.BTN_START, 1),
        }

        self._setup_ui()

    def _action_label(self, code: int) -> str:
        return ACTION_MAP.get(code, "")

    def _dpad_action_label(self, code: int, val: int) -> str:
        axis = DPAD_ABS_MAP.get(code, {})
        return axis.get(val, "")

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout()
        top_layout = QGridLayout()

        top_layout.addWidget(self._create_dual_btn("LT", "L2"), 0, 0)
        top_layout.addWidget(self._create_dual_btn("RT", "R2"), 0, 2)
        top_layout.addWidget(self._create_dual_btn("LB", "L1"), 1, 0)
        top_layout.addWidget(self._create_dual_btn("RB", "R1"), 1, 2)
        top_layout.setColumnStretch(1, 1)

        mid_layout = QHBoxLayout()

        dpad_grid = QGridLayout()
        dpad_grid.addWidget(self._make_dpad_btn("▲", e.ABS_HAT0Y, -1), 0, 1)
        dpad_grid.addWidget(self._make_dpad_btn("◀", e.ABS_HAT0X, -1), 1, 0)
        dpad_grid.addWidget(self._make_dpad_btn("▶", e.ABS_HAT0X, 1), 1, 2)
        dpad_grid.addWidget(self._make_dpad_btn("▼", e.ABS_HAT0Y, 1), 2, 1)

        center_vbox = QVBoxLayout()
        center_vbox.addStretch()
        center_vbox.addWidget(self._create_dual_btn("Guide", "PS", "#444"))
        center_vbox.addWidget(self._create_dual_btn("Back", "Share", "#444"))
        center_vbox.addWidget(self._create_dual_btn("Start", "Opt", "#444"))
        center_vbox.addStretch()

        actions_grid = QGridLayout()
        actions_grid.addWidget(self._create_dual_btn("Y", "△"), 0, 1)
        actions_grid.addWidget(self._create_dual_btn("X", "□"), 1, 0)
        actions_grid.addWidget(self._create_dual_btn("B", "○"), 1, 2)
        actions_grid.addWidget(self._create_dual_btn("A", "✕"), 2, 1)

        mid_layout.addLayout(dpad_grid)
        mid_layout.addStretch()
        mid_layout.addLayout(center_vbox)
        mid_layout.addStretch()
        mid_layout.addLayout(actions_grid)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(140)
        self.console.setStyleSheet(
            "background-color: #121212; color: #00FF41; border: 1px solid #333;"
        )
        self.console.append("  Event Stream — use botões ou teclado (↑↓←→/Z/X/Space)")
        self.console.append("")

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(mid_layout)
        main_layout.addSpacing(20)
        main_layout.addWidget(QLabel("Event Stream (Raw Evdev):"))
        main_layout.addWidget(self.console)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.setStyleSheet("""
            QPushButton {
                min-width: 80px; min-height: 50px;
                background: #2b2b2b; color: #eee; border-radius: 6px;
                font-family: 'Segoe UI', sans-serif; font-size: 12px;
            }
            QPushButton:pressed, QPushButton[active="true"] {
                background: #005a9e; border: 2px solid #00a4ef;
            }
        """)

    def _create_dual_btn(
        self, xbox_label: str, ps_label: str, color: str | None = None
    ) -> QPushButton:
        display_text = f"{xbox_label}\n({ps_label})"
        code = next(item[2] for item in self.button_configs if item[0] == xbox_label)
        btn = QPushButton(display_text)
        if color:
            btn.setStyleSheet(f"background-color: {color};")

        btn.pressed.connect(
            lambda: self._trigger_btn(f"{xbox_label}/{ps_label}", code, 1)
        )
        btn.released.connect(
            lambda: self._trigger_btn(f"{xbox_label}/{ps_label}", code, 0)
        )

        self.button_map[code] = btn
        return btn

    def _make_dpad_btn(self, label: str, axis: int, val: int) -> QPushButton:
        btn = QPushButton(label)
        btn.pressed.connect(lambda: self._trigger_axis(label, axis, val))
        btn.released.connect(lambda: self._trigger_axis(label, axis, 0))
        self.button_map[axis + val] = btn  # chave única para visual
        return btn

    def _trigger_btn(self, label: str, code: int, val: int) -> None:
        self.ui.write(e.EV_KEY, code, val)
        self.ui.syn()
        action = self._action_label(code)
        action_str = f" → [{action}]" if action else ""
        direction = "PRESSED" if val else "RELEASED"
        msg = f"{direction:<10} | {label:<12} | CODE: {code}{action_str}"
        self._log(msg)

    def _trigger_axis(self, label: str, axis: int, val: int) -> None:
        self.ui.write(e.EV_ABS, axis, val)
        self.ui.syn()
        action = self._dpad_action_label(axis, val)
        action_str = f" → [{action}]" if action else ""
        direction = "PRESSED" if val != 0 else "RELEASED"
        msg = f"{direction:<10} | {label:<4}         | AXIS: {axis} VAL: {val:+d}{action_str}"
        self._log(msg)

    def _log(self, msg: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.console.append(f"[{timestamp}] {msg}")
        self.console.moveCursor(QTextCursor.End)

    # --- Lógica do Teclado ---

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        key = event.key()
        if key in self.keyboard_map:
            ev_type, code, val = self.keyboard_map[key]

            self.ui.write(ev_type, code, val)
            self.ui.syn()

            if ev_type == e.EV_KEY:
                btn_code = code
            else:
                btn_code = code + val

            if btn_code in self.button_map:
                btn = self.button_map[btn_code]
                btn.setProperty("active", "true")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        key = event.key()
        if key in self.keyboard_map:
            ev_type, code, val = self.keyboard_map[key]
            self.ui.write(ev_type, code, 0)
            self.ui.syn()

            if ev_type == e.EV_KEY:
                btn_code = code
            else:
                btn_code = code + val

            if btn_code in self.button_map:
                btn = self.button_map[btn_code]
                btn.setProperty("active", "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DualGamepad()
    window.show()
    sys.exit(app.exec())
