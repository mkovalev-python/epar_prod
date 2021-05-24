# -*- coding:utf-8 -*-
__author__ = 'Tonakai'

import copy
import datetime

from django.http import Http404
from django.utils import timezone

from PManager.classes.datetime.work_time import WorkTime
from PManager.models.tasks import PM_Task_Status, PM_Task, PM_Milestone
from PManager.services.access import project_access


def get_projects(user, current_project):
    if current_project:
        if not project_access(current_project.id, user.id):
            raise Http404
        return [current_project]
    else:
        return user.get_profile().getProjects()


def project_columns(project, colors, statuses):
    projectSettings = project.getSettings()
    columns = []
    if projectSettings.get('use_colors_in_kanban', False):
        for color_code, color in colors:
            settingColor = 'color_name_' + color_code
            if settingColor in projectSettings and projectSettings[settingColor]:
                columns.append({'code': color_code, 'name': projectSettings[settingColor], 'prop': 'color'})
    else:
        newStatus = False
        for status in statuses:
            status.update({'prop': 'status'})
            if status['code'] == 'ready':
                status['name'] = u'На проверке'

            if status['code'] == 'revision':
                status['name'] = u'В работе'

                newStatus = copy.copy(status)
                newStatus['code'] = 'closed'
                newStatus['name'] = u'Закрыта'

            columns.append(status)
        if newStatus:
            columns.append(newStatus)

    return (columns, projectSettings.get('use_colors_in_kanban', False))


def project_to_kanban_project(project, columns):
    setattr(project, 'columns', columns)
    setattr(project, 'date_init', project.dateCreate)
    setattr(project, 'user_source', project.getUsers())
    return project


def get_statuses():
    return [status.__dict__ for status in PM_Task_Status.objects.all().order_by('-id')]


def widget(request, headerValues, widgetParams={}, qArgs=[]):
    current_project = headerValues['CURRENT_PROJECT']
    statuses = get_statuses()
    # unknown purpose
    arColorsByProject = {}
    colors = PM_Task.colors
    # raising Http404 if user has no access to current_project
    projects = get_projects(request.user, current_project)
    for project in projects:
        (columns, use_colors) = project_columns(project, colors, statuses)
        project_to_kanban_project(project, columns)
        setattr(project, 'use_colors', use_colors)
        setattr(project, 'all_milestones', project.milestones.order_by('-date'))

        current_milestone = widgetParams.get('currentMilestone')

        if not current_milestone and request.GET.get('milestone'):
            current_milestone = PM_Milestone.objects.filter(project=project, pk=int(request.GET.get('milestone', 0)))

        if current_milestone is None or not current_milestone.exists():
            current_milestone = PM_Milestone.objects.filter(
                closed=False,
                date__gt=datetime.datetime.now(),
                project=project
            ).order_by('date')

        if current_milestone is None or not current_milestone.exists():
            current_milestone = PM_Milestone.objects.filter(
                project=project,
                closed=False
            ).order_by('date_create')

        if current_milestone.count():
            current_milestone = current_milestone[0]

            aTaskTime = {}
            aClosedTaskTime = {}
            aClosedAndReadyTaskTime = {}
            aAllTime = {}
            aElapsedTime = {}
            aResps = []
            aRespsId = []

            allTimeAllResps = 0
            elapsedTimeAllResps = 0
            taskTimeAllResps = 0
            closedTaskTimeAllResps = 0
            closedAndReadyTimeAllResps = 0

            for task in current_milestone.tasks.filter(active=True):
                if task.resp:
                    if task.resp.id not in aTaskTime:
                        aTaskTime[task.resp.id] = 0

                    if task.resp.id not in aClosedTaskTime:
                        aClosedTaskTime[task.resp.id] = 0

                    if task.resp.id not in aClosedAndReadyTaskTime:
                        aClosedAndReadyTaskTime[task.resp.id] = 0

                    if not task.resp.id in aRespsId:
                        aRespsId.append(task.resp.id)
                        aResps.append(task.resp)

                    aTaskTime[task.resp.id] += task.planTime or 0

                    if task.closed:
                        aClosedTaskTime[task.resp.id] += task.planTime or 0
                        aClosedAndReadyTaskTime[task.resp.id] += task.planTime or 0
                    elif task.status and task.status.code == 'ready':
                        aClosedAndReadyTaskTime[task.resp.id] += task.planTime or 0

            for rId in aClosedTaskTime:
                closedTaskTimeAllResps += aClosedTaskTime[rId]

            for rId in aClosedAndReadyTaskTime:
                closedAndReadyTimeAllResps += aClosedAndReadyTaskTime[rId]

            for rId in aTaskTime:
                taskTimeAllResps += aTaskTime[rId]

            timeWorkManager = WorkTime()
            for resp in aResps:
                respHoursPerDay = resp.get_profile().hoursQtyPerDay or None

                aAllTime[resp.id] = timeWorkManager.getTimeBetween(
                    current_milestone.date_create,
                    current_milestone.date,
                    respHoursPerDay
                )

                if current_milestone.date is not None and timezone.make_aware(
                        datetime.datetime.now(), timezone.get_current_timezone()
                ) > current_milestone.date:
                    aElapsedTime[resp.id] = aAllTime[resp.id]
                else:
                    aElapsedTime[resp.id] = timeWorkManager.getTimeBetween(
                        current_milestone.date_create,
                        timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone()),
                        respHoursPerDay
                    )

                allTimeAllResps += aAllTime[resp.id]
                elapsedTimeAllResps += aElapsedTime[resp.id]

            setattr(current_milestone, 'aTaskTime', aTaskTime)
            setattr(current_milestone, 'aElapsedTime', aElapsedTime)
            setattr(current_milestone, 'aAllTime', aAllTime)

            setattr(current_milestone, 'allTimeAllResps', float(allTimeAllResps))
            setattr(current_milestone, 'elapsedTimeAllResps', float(elapsedTimeAllResps))
            setattr(current_milestone, 'elapsedTimeAllRespsPercent',
                    int(round(float(elapsedTimeAllResps) * 100 / allTimeAllResps, 2) if allTimeAllResps else 0))
            setattr(current_milestone, 'taskTimeAllResps', float(taskTimeAllResps))
            setattr(current_milestone, 'closedTaskTimeAllResps', float(closedTaskTimeAllResps))
            setattr(current_milestone, 'closedTaskTimeAllRespsPercent',
                    int(round(float(closedTaskTimeAllResps) * 100 / taskTimeAllResps, 2) if taskTimeAllResps else 0))

            setattr(current_milestone, 'closedAndReadyTimeAllResps', float(closedAndReadyTimeAllResps))
            setattr(current_milestone, 'closedAndReadyTimeAllRespsPercent', int(
                round(float(closedAndReadyTimeAllResps) * 100 / taskTimeAllResps, 2) if taskTimeAllResps else 0))

            setattr(project, 'current_milestone', current_milestone)

    return {
        'projects_data': projects,
        'title': u'Канбан',
        'current_project': current_project,
        'use_colors': use_colors,
        'arColorsByProject': arColorsByProject,
    }
