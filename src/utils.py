import logging

import psutil

logger = logging.getLogger(__name__)


def check_running_processes(search_process: list[str]) -> list[str]:
    if not search_process:
        return []

    search_lower = [p.lower() for p in search_process]
    running: list[str] = []

    for proc in psutil.process_iter(["name"]):
        try:
            name = proc.info["name"]
            if name and name.lower() in search_lower:
                running.append(name.lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return running
