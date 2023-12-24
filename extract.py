#!/bin/python3

import json
import logging
from typing import List, Dict, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_projects(json_backup: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extracts project data from a JSON backup.

    :param json_backup: The JSON object containing the backup data.
    :return: A list of projects with their IDs and titles.
    """
    if 'project' not in json_backup or 'entities' not in json_backup['project']:
        logging.error(f"Invalid JSON structure for projects. {json_backup}")
        return []

    projects = []
    required_keys = {'id', 'title'}
    for project in json_backup['project']['entities'].values():
        if any(key not in project for key in required_keys):
            logging.warning(f"Missing 'id' or 'title' in project: {project}")
            continue

        projects.append(
                {
                    'project_id': project['id'],
                    'project_title': project['title']
                }
        )

    return projects


def extract_tasks(
        json_backup: Dict[str, Any]
) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
    """
    Extracts task data and time spent on tasks from a JSON backup.

    :param json_backup: The JSON object containing the backup data.
    :return: A tuple containing two lists:
             - The first list consists of dictionaries with task information
             (project_id, task_id, task_title).
             - The second list consists of dictionaries with time spent on each
             task (task_id, date, time_spent_ms).
    """
    if 'task' not in json_backup or 'entities' not in json_backup['task']:
        logging.error(f"Invalid JSON structure for tasks. {json_backup}")
        return [], []

    tasks = []
    time_spent = []
    required_keys = {'id', 'title', 'projectId', 'timeSpentOnDay'}
    for task in json_backup['task']['entities'].values():
        if any(key not in task for key in required_keys):
            logging.warning(f"Missing 'id', 'title', 'projectId', "
                            f"or 'timeSpentOnDay' in task: {task}")
            continue

        task_info = {
            'project_id': task['projectId'],
            'task_id': task['id'],
            'task_title': task['title'],
        }
        tasks.append(task_info)

        for date, time_spent_ms in task['timeSpentOnDay'].items():
            time_spent_entry = {
                'task_id': task['id'],
                'date': date,
                'time_spent_ms': time_spent_ms
            }
            time_spent.append(time_spent_entry)

    return tasks, time_spent


def extract(
        filepath: str
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, Any]]]:
    """
    Extracts project, task, and time spent data from a JSON file.

    :param filepath: The file path of the JSON backup.
    :return: A tuple containing three lists:
             - The first list contains dictionaries with project
             information (project_id, project_title).
             - The second list contains dictionaries with task
             information (project_id, task_id, task_title).
             - The third list contains dictionaries with time spent on each
             task (task_id, date, time_spent_ms).
    """
    try:
        with open(filepath, 'r') as fp:
            backup = json.load(fp)

        projects = extract_projects(backup)
        tasks, time_spent = extract_tasks(backup)

        return projects, tasks, time_spent

    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {filepath}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    return [], [], []


if __name__ == '__main__':
    projects, tasks, time_spent = extract("backups/2023-12-23.json")

    print(projects, tasks)

