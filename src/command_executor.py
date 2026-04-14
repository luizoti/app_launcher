import logging
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
        # Pega a lista processada corretamente
        args_list = __command_processor(command)

        subprocess.Popen(
            args=args_list,
            # stdout=subprocess.DEVNULL,
            # stderr=subprocess.DEVNULL,
            shell=False,
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
        # shlex.split entende aspas!
        # Ele transforma "app 'Pegasus'" em ['app', 'Pegasus'] (removendo as aspas inúteis)
        return shlex.split(command)
    return command
