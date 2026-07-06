#!/usr/bin/env python3
"""CLI controller — envia eventos UInput para testar app_launcher.

Usage:
    python scripts/simulate_cli.py <action> [--hold]

Actions:
    enter         Botão A (304)  → launch app
    toggle_view   Botão Guide    → show/hide janela
    up            Dpad cima
    down          Dpad baixo
    left          Dpad esquerda
    right         Dpad direita

    --list        Lista ações disponíveis
    --hold        Segura o botão (não solta automaticamente)
"""

import argparse
import sys
import time

from evdev import UInput
from evdev import ecodes as e
from evdev.device import AbsInfo

# Mapeamento ação → (ev_type, code, value_press, value_release)
KEY_ACTIONS: dict[str, tuple[int, int]] = {
    "enter": (e.EV_KEY, e.BTN_A),
    "toggle_view": (e.EV_KEY, e.BTN_MODE),
}

ABS_ACTIONS: dict[str, tuple[int, int, int]] = {
    "up": (e.EV_ABS, e.ABS_HAT0Y, -1),
    "down": (e.EV_ABS, e.ABS_HAT0Y, 1),
    "left": (e.EV_ABS, e.ABS_HAT0X, -1),
    "right": (e.EV_ABS, e.ABS_HAT0X, 1),
}

ALL_ACTIONS: list[str] = list(KEY_ACTIONS) + list(ABS_ACTIONS)


def list_actions() -> None:
    print("Ações disponíveis:")
    for a in ALL_ACTIONS:
        if a in KEY_ACTIONS:
            code = KEY_ACTIONS[a][1]
            print(f"  {a:<14} → EV_KEY code={code}")
        else:
            axis = ABS_ACTIONS[a][1]
            val = ABS_ACTIONS[a][2]
            print(f"  {a:<14} → EV_ABS axis={axis} val={val:+d}")
    print()
    print("Flags:  --hold  não solta o botão")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", help="Ação a executar")
    parser.add_argument("--list", action="store_true", help="Lista ações")
    parser.add_argument(
        "--hold", action="store_true", help="Segura o botão (não solta)"
    )
    args = parser.parse_args()

    if args.list:
        list_actions()
        return

    if not args.action:
        parser.print_help()
        sys.exit(1)

    action = args.action.lower()

    if action not in ALL_ACTIONS:
        print(f"Erro: ação desconhecida '{action}'")
        print("Use --list para ver as ações disponíveis")
        sys.exit(1)

    ui = UInput(
        {
            e.EV_KEY: [e.BTN_A, e.BTN_MODE],
            e.EV_ABS: [
                (e.ABS_HAT0X, AbsInfo(0, -1, 1, 0, 0, 0)),
                (e.ABS_HAT0Y, AbsInfo(0, -1, 1, 0, 0, 0)),
            ],
        },
        name="Virtual Joystick",
    )

    try:
        if action in KEY_ACTIONS:
            ev_type, code = KEY_ACTIONS[action]
            ui.write(ev_type, code, 1)
            ui.syn()
            print(f"Enviado: {action} (EV_KEY code={code} pressed)")
            if not args.hold:
                time.sleep(0.05)
                ui.write(ev_type, code, 0)
                ui.syn()
                print(f"Enviado: {action} (EV_KEY code={code} released)")
        else:
            ev_type, axis, val = ABS_ACTIONS[action]
            ui.write(ev_type, axis, val)
            ui.syn()
            print(f"Enviado: {action} (EV_ABS axis={axis} val={val:+d})")
            if not args.hold:
                time.sleep(0.1)
                ui.write(ev_type, axis, 0)
                ui.syn()
                print(f"Enviado: {action} (EV_ABS axis={axis} val=0)")
    finally:
        if not args.hold:
            ui.close()


if __name__ == "__main__":
    main()
