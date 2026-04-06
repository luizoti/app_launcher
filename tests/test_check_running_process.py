import unittest

from setproctitle import setproctitle

from src.utils import check_running_processes


def create_process(process_list: list[str]):
    for process in process_list:
        setproctitle(process)


class TestCheckRunningProcess(unittest.TestCase):
    def setUp(self):
        self.process_list: list[str] = ["kodi", "emulationstation"]

    def test_one_running_process(self):
        create_process(process_list=self.process_list)
        current_process = check_running_processes(search_process=self.process_list)
        self.assertIn(self.process_list[0], current_process)

    def test_two_running_process(self):
        create_process(process_list=self.process_list)
        current_process = check_running_processes(search_process=self.process_list)
        self.assertEqual(self.process_list, current_process)

    def test_get_case_insensitive_process(self):
        process_names = ["kodi", "emulationstation"]
        create_process(process_list=[x.capitalize() for x in process_names])
        current_process = check_running_processes(search_process=process_names)
        self.assertEqual(process_names, current_process)

    def test_get_case_insensitive_search(self):
        process_names = ["kodi", "emulationstation"]
        create_process(process_list=process_names)
        current_process = check_running_processes(
            search_process=[x.capitalize() for x in process_names]
        )
        self.assertEqual(process_names, current_process)


if __name__ == "__main__":
    unittest.main()
