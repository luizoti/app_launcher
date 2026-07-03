import logging
import shlex
import subprocess

import psutil

logger = logging.getLogger(__name__)


def check_running_processes(search_process: list[str]) -> list[str]:
    if not search_process:
        return []

    search_lower = [p.lower() for p in search_process]
    matched: set[str] = set()

    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            name = (proc.info["name"] or "").lower()
            cmdline = " ".join(proc.info.get("cmdline") or []).lower()
            for term_lower, term_orig in zip(search_lower, search_process):
                if term_lower in name or term_lower in cmdline:
                    matched.add(term_orig)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return list(matched)


def _extract_process_name(cmd: list[str] | str) -> str:
    """Extract the likely target process name from a launcher command.

    For wrapped commands (e.g. ``x-terminal-emulator -e emulationstation``)
    this returns the inner app name. Otherwise returns the executable basename.
    """
    parts = cmd if isinstance(cmd, list) else shlex.split(cmd)
    for flag in ("-e", "-c", "--command", "--exec"):
        if flag in parts:
            idx = parts.index(flag)
            if idx + 1 < len(parts):
                return parts[idx + 1]
    return parts[0].rsplit("/", 1)[-1]


def _focus_process(search: str) -> bool:
    """Find a running process matching *search* and bring its window to front.

    Returns ``True`` if found and focused, ``False`` otherwise.
    """
    search_lower = search.lower()
    pid: int | None = None

    for proc in psutil.process_iter(["name", "cmdline", "pid"]):
        try:
            name = (proc.info.get("name") or "").lower()
            cmdline = " ".join(proc.info.get("cmdline") or []).lower()
            if search_lower in name or search_lower in cmdline:
                pid = proc.info["pid"]
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if pid is None:
        return False

    try:
        subprocess.run(
            ["xdotool", "search", "--pid", str(pid), "windowactivate"],
            capture_output=True,
            timeout=2,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        result = subprocess.run(
            ["wmctrl", "-l", "-p"], capture_output=True, text=True, timeout=2
        )
        for line in result.stdout.splitlines():
            parts = line.split(None, 2)
            if len(parts) >= 2 and parts[1] == str(pid):
                subprocess.run(
                    ["wmctrl", "-i", "-a", parts[0]],
                    capture_output=True,
                    timeout=2,
                )
                return True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    return False
