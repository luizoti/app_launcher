import base64
import typing
from pathlib import Path

import psutil



def check_running_processes(search_process: str):
    if not search_process:
        raise ValueError("Argument `search_process` cannot be None")

    return (
        x
        for x in [x.info["name"].lower() for x in psutil.process_iter(["name"])]
        if x in [process.lower() for process in search_process]
    )
