import subprocess
import traceback


class CommandExecutor:
    def __init__(self, command: list[str], label_changer=None):
        self.command = command
        self.label_changer = label_changer

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
            self.label_changer(f"Comando não encontrado: {file_not_found_error}")
        except Exception:
            print(traceback.format_exc())
