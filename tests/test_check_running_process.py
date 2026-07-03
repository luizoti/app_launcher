import unittest
from unittest.mock import MagicMock, patch

from src.utils import check_running_processes


class TestCheckRunningProcess(unittest.TestCase):
    def _make_process(self, name: str, cmdline: list[str] | None = None) -> MagicMock:
        proc = MagicMock()
        proc.info = {"name": name, "cmdline": cmdline or [name]}
        return proc

    @patch("src.utils.psutil.process_iter")
    def test_returns_matching_processes(self, mock_process_iter):
        mock_process_iter.return_value = [
            self._make_process("kodi"),
            self._make_process("emulationstation"),
            self._make_process("python"),
        ]
        result = list(
            check_running_processes(search_process=["kodi", "emulationstation"])
        )
        self.assertCountEqual(result, ["kodi", "emulationstation"])

    @patch("src.utils.psutil.process_iter")
    def test_returns_empty_when_none_match(self, mock_process_iter):
        mock_process_iter.return_value = [
            self._make_process("firefox"),
            self._make_process("python"),
        ]
        result = list(check_running_processes(search_process=["kodi"]))
        self.assertEqual(result, [])

    @patch("src.utils.psutil.process_iter")
    def test_case_insensitive_process_name(self, mock_process_iter):
        mock_process_iter.return_value = [
            self._make_process("Kodi"),
            self._make_process("EMULATIONSTATION"),
        ]
        result = list(
            check_running_processes(search_process=["kodi", "emulationstation"])
        )
        self.assertCountEqual(result, ["kodi", "emulationstation"])

    @patch("src.utils.psutil.process_iter")
    def test_case_insensitive_search(self, mock_process_iter):
        mock_process_iter.return_value = [
            self._make_process("kodi"),
        ]
        result = list(check_running_processes(search_process=["Kodi"]))
        self.assertEqual(result, ["Kodi"])

    @patch("src.utils.psutil.process_iter")
    def test_matches_via_cmdline_wrapper(self, mock_process_iter):
        mock_process_iter.return_value = [
            self._make_process(
                "x-terminal-emulator",
                cmdline=["x-terminal-emulator", "-e", "emulationstation"],
            ),
        ]
        result = check_running_processes(search_process=["emulationstation"])
        self.assertEqual(result, ["emulationstation"])

    @patch("src.utils.psutil.process_iter")
    def test_matches_substring_in_cmdline(self, mock_process_iter):
        mock_process_iter.return_value = [
            self._make_process("moonlight-qt", cmdline=["moonlight-qt"]),
        ]
        result = check_running_processes(search_process=["moonlight"])
        self.assertEqual(result, ["moonlight"])

    @patch("src.utils.psutil.process_iter")
    def test_deduplicates_matches(self, mock_process_iter):
        mock_process_iter.return_value = [
            self._make_process("kodi", cmdline=["kodi"]),
            self._make_process("firefox", cmdline=["kodi-wayland"]),
        ]
        result = check_running_processes(search_process=["kodi"])
        self.assertEqual(result, ["kodi"])

    @patch("src.utils.psutil.process_iter")
    def test_no_match_when_term_absent(self, mock_process_iter):
        mock_process_iter.return_value = [
            self._make_process("firefox", cmdline=["firefox", "https://x.com"]),
        ]
        result = check_running_processes(search_process=["kodi", "emulationstation"])
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
