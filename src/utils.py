import psutil


def check_running_processes(
    search_process: list[str],
):
    """TODO: Revise this function, this is not used, and the utility is not clear
    anymore i don't if this is useful, but it can be used to check if a
    process is running, and avoid opening the app if the process is already running.
    """
    return (
        x
        for x in [x.info["name"].lower() for x in psutil.process_iter(["name"])]
        if x in [process.lower() for process in search_process]
    )
