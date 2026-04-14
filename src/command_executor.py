import logging
import os
import shlex
import subprocess
import traceback
import typing

logger = logging.getLogger(__name__)


def command_executor(
    command: list[str] | str,
    label_changer: typing.Callable[[str], None] | None = None,
    *_: typing.Any,
):
    try:
        args_list: list[str] = __command_processor(command)
        clean_env: dict[str, str] = os.environ.copy()
        bad_vars: list[str] = [
            "LD_LIBRARY_PATH",
            "QT_PLUGIN_PATH",
            "QT_QPA_PLATFORM_PLUGIN_PATH",
            "PYTHONPATH",
            "PYTHONHOME",
        ]
        for var in bad_vars:
            clean_env.pop(var, None)

        if "DISPLAY" not in clean_env:
            clean_env["DISPLAY"] = ":0"

        subprocess.Popen(
            args=args_list,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
            env=clean_env,
        )
        logging.debug(f"Command executed `{command}`")

    except FileNotFoundError as file_not_found_error:
        message = f"Command not found: {file_not_found_error}"
        logging.error(message)
        if label_changer:
            label_changer(message)
    except Exception:
        logging.exception(traceback.format_exc())


def __command_processor(
    command: list[str] | str,
) -> list[str]:
    if isinstance(command, str):
        return shlex.split(command)
    return command
