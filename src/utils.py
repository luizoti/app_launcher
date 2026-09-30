import logging
import os
import shlex
import subprocess

import psutil

logger = logging.getLogger(__name__)

PROCESS_ATTRS: list[str] = ["name", "cmdline", "status"]

STRIPPED_SUFFIXES: frozenset[str] = frozenset({".exe", ".bin", ".appimage"})

WRAPPER_FLAGS: tuple[str, ...] = ("-e", "-c", "--command", "--exec")


def _norm(token: str) -> str:
    """Normalize a command token into a comparable executable name.

    Strips directories, lowercases and removes well known binary suffixes so
    ``/usr/bin/Kodi.exe`` and ``Kodi`` both normalize to ``kodi``.
    """
    basename = token.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].strip().lower()
    for suffix in STRIPPED_SUFFIXES:
        if basename.endswith(suffix):
            return basename[: -len(suffix)]
    return basename


def _build_terms(search_process: list[str]) -> dict[str, str]:
    """Map normalized search terms to their original spelling."""
    return {_norm(term): term for term in search_process if term.strip()}


def _is_ignorable(proc: psutil.Process) -> bool:
    """Skip zombies, the kernel placeholder and the launcher itself.

    A terminating app lingers as a zombie keeping its name and cmdline, which
    used to block every launch until its parent reaped it.
    """
    if proc.pid in (0, os.getpid()):
        return True
    return proc.info.get("status") == psutil.STATUS_ZOMBIE


def _wrapped_program(argument: str) -> str:
    """Normalized program name of a wrapper argument.

    ``"kodi --standalone"`` -> ``kodi`` and the nested
    ``"x-terminal-emulator -e emulationstation"`` -> ``emulationstation``;
    an unparseable or empty argument -> ``""``.
    """
    try:
        parts = shlex.split(argument)
    except ValueError:
        return ""
    return _norm(_extract_process_name(parts)) if parts else ""


def _candidates(proc: psutil.Process) -> set[str]:
    """Normalized executable names a process can be identified by.

    Only the process own executable and the program handed to a wrapper flag
    count. Plain argv entries are ignored, so ``grep -r kodi .`` or
    ``tail -f kodi.log`` are not mistaken for a running kodi.
    """
    found: set[str] = set()

    name = proc.info.get("name")
    if name:
        found.add(_norm(name))

    cmdline = list(proc.info.get("cmdline") or ())
    for index, token in enumerate(cmdline[:-1]):
        if token in WRAPPER_FLAGS and cmdline[index + 1]:
            wrapped = _wrapped_program(cmdline[index + 1])
            if wrapped:
                found.add(wrapped)

    return found


def _match(proc: psutil.Process, terms: dict[str, str]) -> set[str]:
    """Original terms this process matches, by exact executable-name equality."""
    candidates = _candidates(proc)
    return {original for norm, original in terms.items() if norm in candidates}


def check_running_processes(search_process: list[str]) -> list[str]:
    if not search_process:
        return []

    terms = _build_terms(search_process)
    matched: set[str] = set()

    for proc in psutil.process_iter(PROCESS_ATTRS):
        try:
            if _is_ignorable(proc):
                continue
            matched |= _match(proc, terms)
            if len(matched) == len(terms):
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return list(matched)


def _extract_process_name(cmd: list[str] | str) -> str:
    """Extract the likely target process name from a launcher command.

    For wrapped commands (e.g. ``x-terminal-emulator -e emulationstation``)
    this returns the inner app name. Otherwise returns the executable basename.
    """
    parts = cmd if isinstance(cmd, list) else shlex.split(cmd)
    for flag in WRAPPER_FLAGS:
        if flag in parts:
            idx = parts.index(flag)
            if idx + 1 < len(parts):
                return parts[idx + 1]
    return parts[0].rsplit("/", 1)[-1]


def _focus_process(search: str) -> bool:
    """Find a running process matching *search* and bring its window to front.

    Returns ``True`` if the process was found (even if focusing failed),
    ``False`` if no matching process exists.
    """
    terms = _build_terms([search])
    if not terms:
        return False

    pid: int | None = None

    for proc in psutil.process_iter(PROCESS_ATTRS):
        try:
            if _is_ignorable(proc):
                continue
            if _match(proc, terms):
                pid = proc.pid
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
    except (FileNotFoundError, subprocess.TimeoutExpired):
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
                    break
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass

    return True
