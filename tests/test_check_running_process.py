import os
import unittest
from typing import cast
from unittest.mock import MagicMock, patch

import psutil

from src.utils import (
    _extract_process_name,
    _focus_process,
    _norm,
    check_running_processes,
)


class _VanishingProcess:
    """Stand-in for a process that dies while the iteration is in flight."""

    pid = 4242

    @property
    def info(self) -> dict[str, object]:
        raise psutil.NoSuchProcess(self.pid)


class TestCheckRunningProcess(unittest.TestCase):
    def _make_process(
        self,
        name: str,
        cmdline: list[str] | None = None,
        status: str = psutil.STATUS_RUNNING,
        pid: int = 1000,
    ) -> MagicMock:
        proc = MagicMock()
        proc.pid = pid
        proc.info = {"name": name, "cmdline": cmdline or [name], "status": status}
        return proc

    @patch("src.utils.psutil.process_iter")
    def test_returns_matching_processes(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("kodi", pid=1),
            self._make_process("emulationstation", pid=2),
            self._make_process("python", pid=3),
        ]
        result = list(
            check_running_processes(search_process=["kodi", "emulationstation"])
        )
        self.assertCountEqual(result, ["kodi", "emulationstation"])

    @patch("src.utils.psutil.process_iter")
    def test_returns_empty_when_none_match(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("firefox", pid=1),
            self._make_process("python", pid=2),
        ]
        result = list(check_running_processes(search_process=["kodi"]))
        self.assertEqual(result, [])

    @patch("src.utils.psutil.process_iter")
    def test_case_insensitive_process_name(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("Kodi", pid=1),
            self._make_process("EMULATIONSTATION", pid=2),
        ]
        result = list(
            check_running_processes(search_process=["kodi", "emulationstation"])
        )
        self.assertCountEqual(result, ["kodi", "emulationstation"])

    @patch("src.utils.psutil.process_iter")
    def test_case_insensitive_search(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("kodi", pid=1),
        ]
        result = list(check_running_processes(search_process=["Kodi"]))
        self.assertEqual(result, ["Kodi"])

    @patch("src.utils.psutil.process_iter")
    def test_matches_wrapped_cmdline_token(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                "x-terminal-emulator",
                cmdline=["x-terminal-emulator", "-e", "emulationstation"],
                pid=1,
            ),
        ]
        result = check_running_processes(search_process=["emulationstation"])
        self.assertEqual(result, ["emulationstation"])

    @patch("src.utils.psutil.process_iter")
    def test_matches_absolute_path_cmdline(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                "kodi", cmdline=["/usr/bin/kodi", "--standalone"], pid=1
            ),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, ["kodi"])

    @patch("src.utils.psutil.process_iter")
    def test_matches_stripped_binary_suffix(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("kodi.exe", cmdline=["kodi.exe"], pid=1),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, ["kodi"])

    @patch("src.utils.psutil.process_iter")
    def test_deduplicates_matches(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("kodi", cmdline=["kodi"], pid=1),
            self._make_process("firefox", cmdline=["kodi-wayland"], pid=2),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, ["kodi"])

    @patch("src.utils.psutil.process_iter")
    def test_no_match_when_term_absent(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("firefox", cmdline=["firefox", "https://x.com"], pid=1),
        ]
        result = check_running_processes(search_process=["kodi", "emulationstation"])
        self.assertEqual(result, [])

    @patch("src.utils.psutil.process_iter")
    def test_ignores_zombie_process(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("kodi", status=psutil.STATUS_ZOMBIE, pid=1),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, [])

    @patch("src.utils.psutil.process_iter")
    def test_ignores_own_pid(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                "app_launcher", cmdline=["app_launcher"], pid=os.getpid()
            ),
        ]
        result = check_running_processes(search_process=["app_launcher"])
        self.assertEqual(result, [])

    @patch("src.utils.psutil.process_iter")
    def test_ignores_pid_zero(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("kodi", pid=0),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, [])

    @patch("src.utils.psutil.process_iter")
    def test_no_match_on_plain_argv_mention(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("grep", cmdline=["grep", "-r", "kodi", "."], pid=1),
            self._make_process("less", cmdline=["less", "settings.json"], pid=2),
            self._make_process("tail", cmdline=["tail", "-f", "kodi.log"], pid=3),
            self._make_process("bash", cmdline=["bash", "kodi"], pid=4),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, [])

    @patch("src.utils.psutil.process_iter")
    def test_matches_nested_shell_wrapper(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                "bash",
                cmdline=["bash", "-c", "x-terminal-emulator -e emulationstation"],
                pid=1,
            ),
        ]
        result = check_running_processes(search_process=["emulationstation"])
        self.assertEqual(result, ["emulationstation"])

    @patch("src.utils.psutil.process_iter")
    def test_matches_wrapper_argument_with_flags(
        self, mock_process_iter: MagicMock
    ) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                "x-terminal-emulator",
                cmdline=["x-terminal-emulator", "-e", "kodi --standalone"],
                pid=1,
            ),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, ["kodi"])

    @patch("src.utils.psutil.process_iter")
    def test_wrapper_flag_without_argument(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                "x-terminal-emulator", cmdline=["x-terminal-emulator", "-e"], pid=1
            ),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, [])

    @patch("src.utils.psutil.process_iter")
    def test_no_match_on_reverse_name_containment(
        self, mock_process_iter: MagicMock
    ) -> None:
        mock_process_iter.return_value = [
            self._make_process("moonlight-setup", cmdline=["moonlight-setup"], pid=1),
        ]
        result = check_running_processes(search_process=["moonlight"])
        self.assertEqual(result, [])

    @patch("src.utils.psutil.process_iter")
    def test_empty_search_returns_empty(self, mock_process_iter: MagicMock) -> None:
        mock_process_iter.return_value = [
            self._make_process("kodi", pid=1),
        ]
        self.assertEqual(check_running_processes(search_process=[]), [])

    @patch("src.utils.psutil.process_iter")
    def test_skips_processes_vanishing_during_iteration(
        self, mock_process_iter: MagicMock
    ) -> None:
        mock_process_iter.return_value = [
            cast("psutil.Process", _VanishingProcess()),
            self._make_process("python", pid=2),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, [])


class TestNorm(unittest.TestCase):
    def test_strips_directory_and_case(self) -> None:
        self.assertEqual(_norm("/usr/bin/KoDi"), "kodi")

    def test_strips_windows_separator(self) -> None:
        self.assertEqual(_norm("C:\\Games\\Kodi.exe"), "kodi")

    def test_keeps_dotted_names(self) -> None:
        self.assertEqual(_norm("kodi.log"), "kodi.log")

    def test_strips_appimage_suffix(self) -> None:
        self.assertEqual(_norm("EmulationStation.AppImage"), "emulationstation")


class TestFocusProcess(unittest.TestCase):
    def _make_process(self, info: dict[str, object]) -> MagicMock:
        proc = MagicMock()
        proc.pid = 1
        proc.info = info
        return proc

    @patch("src.utils.subprocess.run")
    @patch("src.utils.psutil.process_iter")
    def test_focuses_exact_match(
        self, mock_process_iter: MagicMock, mock_run: MagicMock
    ) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                {"name": "kodi", "cmdline": ["kodi"], "status": psutil.STATUS_RUNNING}
            ),
        ]
        self.assertTrue(_focus_process("kodi"))
        called_args: list[str] = mock_run.call_args[0][0]
        self.assertEqual(called_args[:2], ["xdotool", "search"])

    @patch("src.utils.subprocess.run")
    @patch("src.utils.psutil.process_iter")
    def test_ignores_zombie_match(
        self, mock_process_iter: MagicMock, mock_run: MagicMock
    ) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                {
                    "name": "kodi",
                    "cmdline": ["kodi"],
                    "status": psutil.STATUS_ZOMBIE,
                }
            ),
        ]
        self.assertFalse(_focus_process("kodi"))
        mock_run.assert_not_called()

    @patch("src.utils.subprocess.run")
    @patch("src.utils.psutil.process_iter")
    def test_ignores_argv_mention(
        self, mock_process_iter: MagicMock, mock_run: MagicMock
    ) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                {
                    "name": "grep",
                    "cmdline": ["grep", "-r", "kodi"],
                    "status": psutil.STATUS_RUNNING,
                }
            ),
        ]
        self.assertFalse(_focus_process("kodi"))
        mock_run.assert_not_called()

    @patch("src.utils.subprocess.run")
    @patch("src.utils.psutil.process_iter")
    def test_empty_search_returns_false(
        self, mock_process_iter: MagicMock, mock_run: MagicMock
    ) -> None:
        mock_process_iter.return_value = [
            self._make_process(
                {"name": "kodi", "cmdline": ["kodi"], "status": psutil.STATUS_RUNNING}
            ),
        ]
        self.assertFalse(_focus_process(""))
        mock_run.assert_not_called()


class TestExtractProcessName(unittest.TestCase):
    def test_wrapper_with_e_flag(self) -> None:
        cmd = ["x-terminal-emulator", "-e", "emulationstation"]
        self.assertEqual(_extract_process_name(cmd), "emulationstation")

    def test_plain_executable_string(self) -> None:
        self.assertEqual(
            _extract_process_name("/usr/bin/moonlight-qt stream nitro app 'Pegasus'"),
            "moonlight-qt",
        )

    def test_plain_executable_list(self) -> None:
        self.assertEqual(
            _extract_process_name(["/usr/bin/firefox", "https://x.com"]),
            "firefox",
        )

    def test_simple_string(self) -> None:
        self.assertEqual(_extract_process_name("subl"), "subl")


if __name__ == "__main__":
    unittest.main()
