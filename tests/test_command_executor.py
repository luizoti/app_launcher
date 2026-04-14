from unittest.mock import MagicMock, patch

import pytest

from src.command_executor import (
    ELEVATION_COMMANDS,
    SHELL_COMMANDS,
    CommandBlockedError,
    CommandExecutor,
    CommandValidator,
    EnvironmentCleaner,
    InvalidArgumentError,
    ProcessRunner,
    RootExecutionError,
)


class TestCommandValidator:
    @pytest.mark.parametrize(
        "command",
        [
            None,
            "",
            [],
        ],
    )
    def test_invalid_argument_raises_error(self, command):
        validator = CommandValidator()
        with pytest.raises(InvalidArgumentError):
            validator.validate(command)

    def test_none_command_raises_error(self):
        validator = CommandValidator()
        with pytest.raises(InvalidArgumentError) as exc_info:
            validator.validate(None)
        assert "None" in str(exc_info.value)

    def test_empty_command_raises_error(self):
        validator = CommandValidator()
        with pytest.raises(InvalidArgumentError) as exc_info:
            validator.validate("")
        assert "empty" in str(exc_info.value)

    @patch("src.command_executor.os.getuid")
    def test_block_root_user(self, mock_getuid):
        mock_getuid.return_value = 0
        validator = CommandValidator()
        with pytest.raises(RootExecutionError) as exc_info:
            validator.validate("kodi")
        assert "root" in str(exc_info.value).lower()

    @patch("src.command_executor.os.getuid")
    def test_allowed_command_when_not_root(self, mock_getuid):
        mock_getuid.return_value = 1000
        validator = CommandValidator()
        validator.validate("kodi")

    @pytest.mark.parametrize("shell_cmd", SHELL_COMMANDS)
    def test_block_shell_commands(self, shell_cmd):
        validator = CommandValidator()
        with pytest.raises(CommandBlockedError) as exc_info:
            validator.validate(shell_cmd)
        assert shell_cmd in str(exc_info.value)

    @pytest.mark.parametrize("elevation_cmd", ELEVATION_COMMANDS)
    def test_block_elevation_commands(self, elevation_cmd):
        validator = CommandValidator()
        with pytest.raises(CommandBlockedError) as exc_info:
            validator.validate(elevation_cmd)
        assert elevation_cmd in str(exc_info.value)


class TestEnvironmentCleaner:
    def test_removes_bad_env_vars(self):
        cleaner = EnvironmentCleaner()
        env = {
            "PATH": "/usr/bin",
            "LD_LIBRARY_PATH": "/usr/lib",
            "QT_PLUGIN_PATH": "/usr/lib/qt",
            "PYTHONPATH": "/usr/lib/python",
        }
        result = cleaner.clean(env)

        assert "PATH" in result
        assert "LD_LIBRARY_PATH" not in result
        assert "QT_PLUGIN_PATH" not in result
        assert "PYTHONPATH" not in result

    def test_sets_display_if_missing(self):
        cleaner = EnvironmentCleaner()
        env = {"PATH": "/usr/bin"}
        result = cleaner.clean(env)

        assert "DISPLAY" in result
        assert result["DISPLAY"] == ":0"

    def test_preserves_existing_display(self):
        cleaner = EnvironmentCleaner()
        env = {"PATH": "/usr/bin", "DISPLAY": ":1"}
        result = cleaner.clean(env)

        assert result["DISPLAY"] == ":1"


class TestProcessRunner:
    @patch("src.command_executor.subprocess.Popen")
    def test_runs_with_env(self, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        runner = ProcessRunner()
        runner.run(args=["kodi"], env={"PATH": "/usr/bin"}, timeout=3)

        mock_popen.assert_called_once()
        call_kwargs = mock_popen.call_args.kwargs
        assert call_kwargs["args"] == ["kodi"]
        assert call_kwargs["env"] == {"PATH": "/usr/bin"}
        assert call_kwargs["shell"] is False


class TestCommandExecutor:
    @patch("src.command_executor.os.getuid")
    def test_valid_command_allowed(self, mock_getuid):
        mock_getuid.return_value = 1000

        mock_runner = MagicMock()
        executor = CommandExecutor(
            validator=CommandValidator(),
            env_cleaner=EnvironmentCleaner(),
            process_runner=mock_runner,
        )

        executor.execute("kodi")

        mock_runner.run.assert_called_once()

    @patch("src.command_executor.os.getuid")
    def test_blocked_command_calls_label_changer(self, mock_getuid):
        mock_getuid.return_value = 1000
        mock_label = MagicMock()

        executor = CommandExecutor()
        executor.execute("sudo rm -rf /", label_changer=mock_label)

        mock_label.assert_called_once()

    @patch("src.command_executor.os.getuid")
    def test_security_log_on_blocked_command(self, mock_getuid, caplog):
        mock_getuid.return_value = 1000

        executor = CommandExecutor()
        executor.execute("sudo rm -rf /")

        assert any("sudo" in record.message.lower() for record in caplog.records)
        assert any(record.levelname == "ERROR" for record in caplog.records)


class TestBackwardCompatibility:
    @patch("src.command_executor.os.getuid")
    def test_command_executor_function_exists(self, mock_getuid):
        mock_getuid.return_value = 1000

        from src import command_executor

        assert hasattr(command_executor, "command_executor")
        command_executor.command_executor("echo test")
