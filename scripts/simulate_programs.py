#!/usr/bin/env python3
"""Simulate running programs to test block_if_running detection.

Usage:
    python scripts/simulate_programs.py                    # start all
    python scripts/simulate_programs.py --list             # show simulated programs
    python scripts/simulate_programs.py --kill             # stop all
    python scripts/simulate_programs.py retroarch kodi     # start specific
"""

import argparse
import os
import signal
import subprocess
import sys
import time

DEFAULT_PROGRAMS = [
    "kodi",
    "emulationstation",
    "retroarch",
    "firefox",
    "chromium",
]

PID_FILE = "/tmp/simulated_programs.pids"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("programs", nargs="*", help="Programs to simulate")
    parser.add_argument("--list", action="store_true", help="List simulated programs")
    parser.add_argument(
        "--kill", action="store_true", help="Stop all simulated programs"
    )
    return parser.parse_args()


def simulate(programs: list[str]) -> None:
    existing = _load_pids()
    for prog in programs:
        if prog in existing:
            pid = existing[prog]
            if _pid_alive(pid):
                print(f"[{prog}] already running (PID {pid})")
                continue
        proc = subprocess.Popen(
            [prog, "infinity"],
            executable="/usr/bin/sleep",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        existing[prog] = proc.pid
        print(f"[{prog}] started (PID {proc.pid})")
    _save_pids(existing)


def kill_all() -> None:
    pids = _load_pids()
    for prog, pid in list(pids.items()):
        if _pid_alive(pid):
            os.kill(pid, signal.SIGTERM)
            print(f"[{prog}] killed (PID {pid})")
        else:
            print(f"[{prog}] already dead")
    if os.path.exists(PID_FILE):
        os.unlink(PID_FILE)


def list_simulated() -> None:
    pids = _load_pids()
    if not pids:
        print("No simulated programs running")
        return
    print(f"{'Program':<20} PID")
    print("-" * 28)
    for prog, pid in sorted(pids.items()):
        status = f" (PID {pid})" if _pid_alive(pid) else " (dead)"
        print(f"{prog:<20} {status}")


def _load_pids() -> dict[str, int]:
    if not os.path.exists(PID_FILE):
        return {}
    pids: dict[str, int] = {}
    with open(PID_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                pids[parts[0]] = int(parts[1])
    return pids


def _save_pids(pids: dict[str, int]) -> None:
    with open(PID_FILE, "w") as f:
        for prog, pid in sorted(pids.items()):
            f.write(f"{prog} {pid}\n")


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def main() -> None:
    args = parse_args()

    if args.list:
        list_simulated()
        return

    if args.kill:
        kill_all()
        return

    programs = args.programs or DEFAULT_PROGRAMS
    simulate(programs)


if __name__ == "__main__":
    main()
