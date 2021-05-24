# -*- coding:utf-8 -*-
__author__ = 'rayleigh'

from PManager.viewsExt.tools import templateTools
import datetime
from django.utils import timezone


def task_list_prepare(tasks, add_tasks, join_project_name=False):
    for task in tasks:
        task.update(add_tasks[task['id']])
        if 'time' in task:
            task['time'] = templateTools.dateTime.timeFromTimestamp(task['time'])
        if join_project_name and 'project__name' in task and not task.get('parentTask', False):
            task['name'] = task['project__name'] + ": " + task['name']

        if task['deadline']:
            b_deadline_passed = task['deadline'] < timezone.make_aware(datetime.datetime.now(),
                                                                       timezone.get_default_timezone())
            if (b_deadline_passed and not task['closed']) or (
                task['closed'] and task['dateClose'] and task['deadline'] and (
                    task['dateClose'] > task['deadline'])):
                task['overdue'] = True

        if task['dateClose']:
            task['dateClose'] = templateTools.dateTime.convertToSite(task['dateClose'])
        if task['deadline']:
            task['deadline'] = templateTools.dateTime.convertToSite(task['deadline'])
        if 'reminder' in task:
            task['reminder'] = templateTools.dateTime.convertToSite(task['reminder'])
        if 'date' in task['last_message']:
            task['last_message']['date'] = templateTools.dateTime.convertToSite(task['last_message']['date'])

        task['name'] = task['name'].replace('<', "&lt;").replace('>', "&gt;")
    return tasks


def tasks_to_tuple(tasks, add_fields=[]):
    default_fields = [
        'critically',
        'planTime',
        'planTimeRegulator',
        'planTimeMainOrg',
        'realTime',
        'onPlanning',
        'name',
        'text',
        'id',
        'deadline',
        'closed',
        'started',
        'dateClose',
        'number',
        'color'
    ]
    return tasks.values(*(add_fields + default_fields))