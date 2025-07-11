import subprocess
import traceback


class CommandExecutor:
    def __init__(self, command: list[str]):
        self.command = command

    def execute(self):
        try:
            subprocess.Popen(
                args=self.command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"INFO - Executando {self.command}")
        except FileNotFoundError as file_not_found_error:
            print(f"INFO - Comando não encontrado: {file_not_found_error}")
        except Exception:
            print(traceback.format_exc())
