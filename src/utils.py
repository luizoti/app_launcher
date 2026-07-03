import logging

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
