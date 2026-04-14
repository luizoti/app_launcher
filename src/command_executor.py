import logging
import os
import shlex
import subprocess
import traceback
import typing

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 3

BAD_ENV_VARS: list[str] = [
    "LD_LIBRARY_PATH",
    "QT_PLUGIN_PATH",
    "QT_QPA_PLATFORM_PLUGIN_PATH",
    "PYTHONPATH",
    "PYTHONHOME",
]

SHELL_COMMANDS: frozenset[str] = frozenset({"sh", "bash", "zsh", "fish", "dash"})
ELEVATION_COMMANDS: frozenset[str] = frozenset(
    {"sudo", "su", "doas", "pkexec", "gksu", "kdesu"}
)


class CommandError(Exception):
    pass


class CommandBlockedError(CommandError):
    pass


class RootExecutionError(CommandError):
    pass


class InvalidArgumentError(CommandError):
    pass


class CommandValidatorProtocol(typing.Protocol):
    def validate(self, command: list[str] | str) -> None: ...


class ProcessRunnerProtocol(typing.Protocol):
    def run(
        self,
        args: list[str],
        env: dict[str, str],
        timeout: int | None,
    ) -> subprocess.Popen: ...


class EnvironmentCleanerProtocol(typing.Protocol):
    def clean(self, env: dict[str, str]) -> dict[str, str]: ...


class CommandValidator:
    def validate(self, command: list[str] | str) -> None:
        if command is None:
            raise InvalidArgumentError("Command cannot be None")

        args_list = shlex.split(command) if isinstance(command, str) else list(command)

        if not args_list:
            raise InvalidArgumentError("Command cannot be empty")

        if os.getuid() == 0:
            raise RootExecutionError("Execution not allowed for root user (UID 0)")

        self._check_blacklist(args_list)

    def _check_blacklist(self, args_list: list[str]) -> None:
        first_arg = args_list[0].lower()

        if first_arg in SHELL_COMMANDS:
            logger.warning(f"Shell command blocked: {first_arg}")
            raise CommandBlockedError(f"Shell command '{first_arg}' is not allowed")

        if first_arg in ELEVATION_COMMANDS:
            logger.warning(f"Elevation command blocked: {first_arg}")
            raise CommandBlockedError(f"Elevation command '{first_arg}' is not allowed")

        if first_arg in ELEVATION_COMMANDS:
            combined = " ".join(args_list[:2])
            logger.warning(f"Elevation command blocked: {combined}")
            raise CommandBlockedError(f"Command '{combined}' is not allowed")


class EnvironmentCleaner:
    def clean(self, env: dict[str, str]) -> dict[str, str]:
        clean_env = env.copy()
        for var in BAD_ENV_VARS:
            clean_env.pop(var, None)

        if "DISPLAY" not in clean_env:
            clean_env["DISPLAY"] = ":0"

        return clean_env


class ProcessRunner:
    def run(
        self,
        args: list[str],
        env: dict[str, str],
        timeout: int | None = None,
    ) -> subprocess.Popen:
        return subprocess.Popen(
            args=args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
            env=env,
        )


class CommandExecutor:
    def __init__(
        self,
        validator: CommandValidatorProtocol | None = None,
        env_cleaner: EnvironmentCleanerProtocol | None = None,
        process_runner: ProcessRunnerProtocol | None = None,
        timeout: int | None = None,
    ):
        self.validator = validator or CommandValidator()
        self.env_cleaner = env_cleaner or EnvironmentCleaner()
        self.process_runner = process_runner or ProcessRunner()
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT_SECONDS

    def execute(
        self,
        command: list[str] | str,
        label_changer: typing.Callable[[str], None] | None = None,
    ) -> None:
        try:
            self.validator.validate(command)

            args_list = _command_processor(command)
            clean_env = self.env_cleaner.clean(os.environ.copy())

            self.process_runner.run(
                args=args_list,
                env=clean_env,
                timeout=self.timeout,
            )

            logger.debug(f"Command executed `{command}`")

        except CommandError as e:
            logger.error(str(e))
            if label_changer:
                label_changer(str(e))
        except Exception:
            logger.exception(traceback.format_exc())


def command_executor(
    command: list[str] | str,
    label_changer: typing.Callable[[str], None] | None = None,
    *_: typing.Any,
):
    executor = CommandExecutor()
    executor.execute(command=command, label_changer=label_changer)


def _command_processor(
    command: list[str] | str,
) -> list[str]:
    if isinstance(command, str):
        return shlex.split(command)
    return list(command)
