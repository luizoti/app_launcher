import logging
import subprocess
import traceback
import typing

logger = logging.getLogger(__name__)
class CommandExecutor:
    def __init__(self, command: typing.Union[list[str], str], label_changer: typing.Optional[typing.Callable[[typing.Text], None]]=None):
        self.command = command
        self.label_changer = label_changer

    def execute(self):
        try:
            subprocess.Popen(
                args=self.__command_processor(self.command),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logging.info(f"INFO - Executando {self.command}")
        except FileNotFoundError as file_not_found_error:
            message = f"Comando não encontrado: {file_not_found_error}"
            logging.error(message)
            if self.label_changer:
                self.label_changer(message)
        except Exception:
            logging.exception(traceback.format_exc())

    @classmethod
    def __command_processor(cls, command: typing.Union[list[str], str]) -> typing.List[typing.Text]:
        if isinstance(command, str):
            command = command.split(" ")
        return command