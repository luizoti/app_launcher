"""Protocols for command execution."""

import subprocess
import typing


class CommandValidatorProtocol(typing.Protocol):
    """Protocol for command validation."""

    def validate(self, command: list[str] | str) -> None: ...


class ProcessRunnerProtocol(typing.Protocol):
    """Protocol for process execution."""

    def run(
        self,
        args: list[str],
        env: dict[str, str],
        timeout: int | None,
    ) -> subprocess.Popen[typing.Any]: ...


class EnvironmentCleanerProtocol(typing.Protocol):
    """Protocol for environment variable cleaning."""

    def clean(self, env: dict[str, str]) -> dict[str, str]: ...
