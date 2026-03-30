import os
from logging import Logger, getLogger

import psutil

logger: Logger = getLogger(__name__)


def create_pid_file_path() -> str:
    pid_file = os.path.join(os.path.expanduser("~"), ".config", "app_launcher.pid")
    logger.debug(f"PID file created: {pid_file}")
    return pid_file


def get_current_pid() -> int:
    return os.getpid()


def check_pid_exist(pid: int) -> bool:
    for process in psutil.process_iter(["name"]):
        if process.pid == pid:
            return True
    return False


def read_pid_file() -> bool | int:
    try:
        with open(create_pid_file_path()) as pid_file:
            return int(pid_file.read())
    except FileNotFoundError:
        return False


def write_pid_file() -> None:
    with open(create_pid_file_path(), "w") as pid_file:
        pid_file.write(f"{get_current_pid()}\n")
        pid_file.close()


def destroy_pid_file() -> None:
    if os.path.exists(create_pid_file_path()):
        os.remove(create_pid_file_path())
        logger.info("PID file destroyed")
