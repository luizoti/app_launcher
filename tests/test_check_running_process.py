import unittest
from unittest.mock import MagicMock, patch

from src.utils import check_running_processes


class TestCheckRunningProcess(unittest.TestCase):
    def _make_process(self, name: str) -> MagicMock:
        proc = MagicMock()
        proc.info = {"name": name}
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
        self.assertEqual(result, ["kodi", "emulationstation"])

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
        self.assertEqual(result, ["kodi", "emulationstation"])

    @patch("src.utils.psutil.process_iter")
    def test_case_insensitive_search(self, mock_process_iter):
        mock_process_iter.return_value = [
            self._make_process("kodi"),
        ]
        result = list(check_running_processes(search_process=["Kodi"]))
        self.assertEqual(result, ["kodi"])


if __name__ == "__main__":
    unittest.main()
