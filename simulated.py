import sys
from datetime import datetime

from evdev import UInput
from evdev import ecodes as e
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


class DualGamepad(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Universal Virtual Controller (Xbox & PS)")
        self.setMinimumWidth(850)

        # Dicionário para guardar as referências dos botões para o efeito visual
        self.button_map = {}

        # Inicializa o dispositivo virtual
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
                    e.BTN_DPAD_UP,
                    e.BTN_DPAD_DOWN,
                    e.BTN_DPAD_LEFT,
                    e.BTN_DPAD_RIGHT,
                ]
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

        # Mapeamento Teclado -> Código Evdev
        self.keyboard_map = {
            Qt.Key_Up: e.BTN_DPAD_UP,
            Qt.Key_Down: e.BTN_DPAD_DOWN,
            Qt.Key_Left: e.BTN_DPAD_LEFT,
            Qt.Key_Right: e.BTN_DPAD_RIGHT,
            Qt.Key_Z: e.BTN_A,  # Exemplo: Z é o botão A
            Qt.Key_X: e.BTN_B,  # Exemplo: X é o botão B
            Qt.Key_Space: e.BTN_START,
        }

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout()
        top_layout = QGridLayout()

        # Adicionando botões e registrando no mapa de botões
        top_layout.addWidget(self._create_dual_btn("LT", "L2"), 0, 0)
        top_layout.addWidget(self._create_dual_btn("RT", "R2"), 0, 2)
        top_layout.addWidget(self._create_dual_btn("LB", "L1"), 1, 0)
        top_layout.addWidget(self._create_dual_btn("RB", "R1"), 1, 2)
        top_layout.setColumnStretch(1, 1)

        mid_layout = QHBoxLayout()

        dpad_grid = QGridLayout()
        dpad_grid.addWidget(self._make_raw_btn("▲", e.BTN_DPAD_UP), 0, 1)
        dpad_grid.addWidget(self._make_raw_btn("◀", e.BTN_DPAD_LEFT), 1, 0)
        dpad_grid.addWidget(self._make_raw_btn("▶", e.BTN_DPAD_RIGHT), 1, 2)
        dpad_grid.addWidget(self._make_raw_btn("▼", e.BTN_DPAD_DOWN), 2, 1)

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
        self.console.setMaximumHeight(120)
        self.console.setStyleSheet(
            "background-color: #121212; color: #00FF41; border: 1px solid #333;"
        )

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
        self, xbox_label: str, ps_label: str, color: str = None
    ) -> QPushButton:
        display_text = f"{xbox_label}\n({ps_label})"
        code = next(item[2] for item in self.button_configs if item[0] == xbox_label)
        btn = QPushButton(display_text)
        if color:
            btn.setStyleSheet(f"background-color: {color};")

        btn.pressed.connect(lambda: self._trigger(f"{xbox_label}/{ps_label}", code, 1))
        btn.released.connect(lambda: self._trigger(f"{xbox_label}/{ps_label}", code, 0))

        # Registra o botão no dicionário usando o código evdev como chave
        self.button_map[code] = btn
        return btn

    def _make_raw_btn(self, label: str, code: int) -> QPushButton:
        btn = QPushButton(label)
        btn.pressed.connect(lambda: self._trigger(label, code, 1))
        btn.released.connect(lambda: self._trigger(label, code, 0))
        self.button_map[code] = btn
        return btn

    def _trigger(self, label: str, code: int, val: int) -> None:
        self.ui.write(e.EV_KEY, code, val)
        self.ui.syn()
        msg = f"{'PRESSED' if val else 'RELEASED':<10} | {label:<12} | HW_CODE: {code}"
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.console.append(f"[{timestamp}] {msg}")
        self.console.moveCursor(QTextCursor.End)

    # --- Lógica do Teclado ---

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        key = event.key()
        if key in self.keyboard_map:
            code = self.keyboard_map[key]
            # Efeito Visual: Força o estado de pressionado via Propriedade Dinâmica
            if code in self.button_map:
                btn = self.button_map[code]
                btn.setProperty("active", "true")
                btn.style().unpolish(btn)  # Atualiza o estilo
                btn.style().polish(btn)
                btn.pressed.emit()  # Dispara a lógica de evdev

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        key = event.key()
        if key in self.keyboard_map:
            code = self.keyboard_map[key]
            # Remove o efeito visual
            if code in self.button_map:
                btn = self.button_map[code]
                btn.setProperty("active", "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)
                btn.released.emit()  # Dispara a lógica de evdev


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DualGamepad()
    window.show()
    sys.exit(app.exec())
