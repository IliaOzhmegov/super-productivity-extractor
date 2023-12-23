#!/bin/python3

import polars as pl
import json

#import pprint.p
from pprint import pprint as print


def parse_projects(json_backup):
    projects = []
    for project in json_backup['project']['entities'].values():

        projects.append(
                {
                    'project_id': project['id'],
                    'project_title': project['title']
                }
        )

    return projects


def parse_tasks(json_backup):
    tasks = []
    for task in backup['task']['entities'].values():
        print(task.keys())
        print(task)

        tasks.append(
                {
                    'project_id': task['projectId'],
                    'task_id': task['id'],
                    'task_title': task['title'],
                }
            )
        break

    return tasks

# with open("backups/2023-11-18.json", 'r') as fp:
with open("backups/2023-12-23.json", 'r') as fp:
    backup = json.load(fp)

    print(parse_projects(backup))
    print('--------------------')
    print('--------------------')
    print('--------------------')
    print('--------------------')
    print(parse_tasks(backup))
