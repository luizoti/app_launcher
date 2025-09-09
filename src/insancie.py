# os.path.join(BASE_DIR, CONFIG_FILE_NAME)
import os

import psutil


def create_pid_file_path():
    return os.path.join(os.path.expanduser("~"), ".config", "startup_ui.pid")


def get_current_pid():
    return os.getpid()


def check_pid_exist(pid):
    for process in psutil.process_iter(["name"]):
        if process.pid == pid:
            return True
    return False


def read_pid_file():
    try:
        with open(create_pid_file_path(), "r") as pid_file:
            return int(pid_file.read())
    except FileNotFoundError:
        return False


def write_pid_file():
    with open(create_pid_file_path(), "w") as pid_file:
        pid_file.write(f"{get_current_pid()}\n")
        pid_file.close()


def destroy_pid_file():
    if os.path.exists(create_pid_file_path()):
        os.remove(create_pid_file_path())
        print("INFO - PID file destroyed")
