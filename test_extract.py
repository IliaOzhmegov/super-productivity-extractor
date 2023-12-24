import unittest
from unittest.mock import patch, mock_open

from extract import extract_projects
from extract import extract_tasks
from extract import extract


class TestExtractProjects(unittest.TestCase):

    def test_extract_projects_valid_data(self):
        json_backup = {
            'project': {
                'entities': {
                    '1': {'id': '1', 'title': 'Project 1'},
                    '2': {'id': '2', 'title': 'Project 2'}
                }
            }
        }
        expected_output = [
            {'project_id': '1', 'project_title': 'Project 1'},
            {'project_id': '2', 'project_title': 'Project 2'}
        ]
        self.assertEqual(extract_projects(json_backup), expected_output)

    @patch('extract.logging')
    def test_extract_projects_invalid_data(self, mock_logging):
        json_backup = {}  # Missing 'task' and 'entities'
        extract_projects(json_backup)

        self.assertEqual(mock_logging.error.call_count, 1)
        calls = [unittest.mock.call("Invalid JSON structure for projects. {}"),]
        mock_logging.error.assert_has_calls(calls, any_order=True)

    @patch('extract.logging')
    def test_extract_projects_partial_data(self, mock_logging):
        json_backup = {
            'project': {
                'entities': {
                    '1': {'id': '1'},  # Missing 'title'
                    '2': {'title': 'Project 2'}  # Missing 'id'
                }
            }
        }
        extract_projects(json_backup)

        self.assertEqual(mock_logging.warning.call_count, 2)
        calls = [
            unittest.mock.call("Missing 'id' or 'title' in project: {'id': '1'}"),
            unittest.mock.call("Missing 'id' or 'title' in project: {'title': 'Project 2'}")
        ]
        mock_logging.warning.assert_has_calls(calls, any_order=True)


class TestExtractTasks(unittest.TestCase):

    def test_extract_tasks_with_valid_data(self):
        json_backup = {
            'task': {
                'entities': {
                    '1': {
                        'id': '1',
                        'projectId': 'p1',
                        'title': 'Task 1',
                        'timeSpentOnDay': {'2023-01-01': 3600000}
                    },
                    '2': {
                        'id': '2',
                        'projectId': 'p2',
                        'title': 'Task 2',
                        'timeSpentOnDay': {'2023-01-02': 7200000}
                    }
                }
            }
        }
        expected_tasks = [
            {'project_id': 'p1', 'task_id': '1', 'task_title': 'Task 1'},
            {'project_id': 'p2', 'task_id': '2', 'task_title': 'Task 2'}
        ]
        expected_time_spent = [
            {'task_id': '1', 'date': '2023-01-01', 'time_spent_ms': 3600000},
            {'task_id': '2', 'date': '2023-01-02', 'time_spent_ms': 7200000}
        ]

        tasks, time_spent = extract_tasks(json_backup)
        self.assertEqual(tasks, expected_tasks)
        self.assertEqual(time_spent, expected_time_spent)

    @patch('extract.logging')
    def test_extract_tasks_with_invalid_structure(self, mock_logging):
        json_backup = {}  # Missing 'task' and 'entities'
        extract_tasks(json_backup)

        self.assertEqual(mock_logging.error.call_count, 1)
        calls = [unittest.mock.call("Invalid JSON structure for tasks. {}"),]
        mock_logging.error.assert_has_calls(calls, any_order=True)

    @patch('extract.logging')
    def test_extract_tasks_with_partial_data(self, mock_logging):
        json_backup = {
            'task': {
                'entities': {
                    '1': {  # Missing 'title'
                        'id': '1', 'projectId': 'p1',
                        'timeSpentOnDay': {'1111-01-01': 100}
                    },
                    '2': {  # Missing 'id'
                        'title': 'Task 2', 'projectId': 'p2',
                        'timeSpentOnDay': {'2222-01-01': 100}
                    },
                    '3': {  # Missing 'timeSpentOnDay'
                        'id': '3', 'title': 'Task 3', 'projectId': 'p3'
                    },
                }
            }
        }
        extract_tasks(json_backup)

        self.assertEqual(mock_logging.warning.call_count, 3)
        calls = [
            unittest.mock.call(
                "Missing 'id', 'title', 'projectId', or 'timeSpentOnDay' in task: "
                "{'id': '1', 'projectId': 'p1', 'timeSpentOnDay': {'1111-01-01': 100}}"
            ),
            unittest.mock.call(
                "Missing 'id', 'title', 'projectId', or 'timeSpentOnDay' in task: "
                "{'title': 'Task 2', 'projectId': 'p2', 'timeSpentOnDay': {'2222-01-01': 100}}"
            ),
            unittest.mock.call(
                "Missing 'id', 'title', 'projectId', or 'timeSpentOnDay' in task: "
                "{'id': '3', 'title': 'Task 3', 'projectId': 'p3'}"
            ),
        ]
        mock_logging.warning.assert_has_calls(calls, any_order=True)


class TestExtractFunction(unittest.TestCase):

    @patch('extract.open', new_callable=mock_open, read_data='{"valid_empty": "json"}')
    @patch('extract.logging')
    def test_extract_with_valid_empty_json_file(self, mock_logging, mock_file):
        projects, tasks, time_spent = extract('valid_path.json')

        self.assertEqual(mock_logging.error.call_count, 2)
        calls = [
            unittest.mock.call( "Invalid JSON structure for projects. {'valid_empty': 'json'}"),
            unittest.mock.call( "Invalid JSON structure for tasks. {'valid_empty': 'json'}"),
        ]
        mock_logging.error.assert_has_calls(calls, any_order=True)

        self.assertEqual(projects, [])
        self.assertEqual(tasks, [])
        self.assertEqual(time_spent, [])

    @patch('extract.open', new_callable=mock_open, read_data='{"valid": "json"}')
    @patch('extract.json.load')
    def test_extract_with_valid_data(self, mock_json_load, mock_file):
        loaded_json = {
            "project": {
                "entities": {
                    "1": {
                        "id": "1",
                        "title": "Project 1"
                    }
                }
            },
            "task": {
                "entities": {
                    "1": {
                        "id": "1",
                        "projectId": "1",
                        "title": "Task 1",
                        "timeSpentOnDay": {
                            "2023-01-01": 3600000
                        }
                    }
                }
            }
        }
        mock_json_load.return_value = loaded_json

        projects, tasks, time_spent = extract('valid_path.json')

        self.assertEqual(projects, [{'project_id': '1', 'project_title': 'Project 1'}])
        self.assertEqual(tasks, [{'task_id': '1', 'project_id': '1', 'task_title': 'Task 1'}])
        self.assertEqual(time_spent, [{'task_id': '1', 'date': '2023-01-01', 'time_spent_ms': 3600000}])

    @patch('extract.logging.error')
    def test_extract_with_invalid_file_path(self, mock_logging_error):
        extract('invalid_path.json')
        mock_logging_error.assert_called_with("File not found: invalid_path.json")

    @patch('extract.open', new_callable=mock_open, read_data='invalid json')
    @patch('extract.logging.error')
    def test_extract_with_invalid_json(self, mock_logging_error, _):
        extract('invalid_json.json')
        mock_logging_error.assert_called_with(
                "Error decoding JSON from invalid_json.json: "
                "Expecting value: line 1 column 1 (char 0)"
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
