import unittest
from setproctitle import setproctitle

from src.utils import check_running_processes


def create_process(process_list: list[str] = None):
    for process in process_list:
        setproctitle(process)


class TestCheckRunningProcess(unittest.TestCase):

    def test_one_running_process(self):
        process_name = "kodi"
        create_process(process_list=[process_name])
        current_process = check_running_processes(search_process=[process_name])
        self.assertIn(process_name, current_process)

    def test_two_running_process(self):
        process_names = ["kodi", "emulationstation"]
        create_process(process_list=process_names)
        current_process = check_running_processes(search_process=process_names)
        self.assertEqual(process_names, current_process)

    def test_get_case_insensitive_process(self):
        process_names = ["kodi", "emulationstation"]
        create_process(process_list=[x.capitalize() for x in process_names])
        current_process = check_running_processes(search_process=process_names)
        self.assertEqual(process_names, current_process)

    def test_get_case_insensitive_search(self):
        process_names = ["kodi", "emulationstation"]
        create_process(process_list=process_names)
        current_process = check_running_processes(search_process=[x.capitalize() for x in process_names])
        self.assertEqual(process_names, current_process)


if __name__ == '__main__':
    unittest.main()
