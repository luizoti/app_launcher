import logging
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
        subprocess.Popen(
            args=__command_processor(command),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logging.info(f"Command executed `{command}`")
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
        command = command.split(" ")
    return command
