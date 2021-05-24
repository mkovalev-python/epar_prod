# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Project, PM_ProjectRoles
import datetime
from django.contrib.auth.models import User
from django.utils import timezone
import random
from PManager.viewsExt.tasks import TaskWidgetManager

def widget(request, headerValues, widgetParams={}, qArgs=[], arPageParams={}):
    date = datetime.datetime.now()
    arWeekdays = {
        'Sun': u'Вс',
        'Mon': u'Пн',
        'Tue': u'Вт',
        'Wed': u'Ср',
        'Thu': u'Чт',
        'Fri': u'Пт',
        'Sat': u'Сб'
    }

    arDates = {}
    arDays = [{
                  'dateFormatted': date.date,
                  'date': date.strftime('%d.%m.%Y'),
                  'weekday': arWeekdays[date.strftime('%a')] + date.strftime(' %d.%m'),
                  'weekdayMark': date.strftime('%a')
              }]

    for i in range(1, 7):
        arDates[i] = date + datetime.timedelta(days=i)
        arDays.append({
            'dateObject': arDates[i],
            'dateFormatted': arDates[i].date,
            'date': arDates[i].strftime('%d.%m.%Y'),
            'weekday': arWeekdays[arDates[i].strftime('%a')] + arDates[i].strftime(' %d.%m'),
            'weekdayMark': arDates[i].strftime('%a')
        })
    arProject = []

    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())

    projects = request.user.get_profile().getProjects()

    for project in projects:
        setattr(project, 'milestoneSet', project.milestones.all())
        setattr(project, 'isManaged', request.user.get_profile().isManager(project))

        for milestone in project.milestoneSet:
            if milestone.date < now and not milestone.closed:
                milestone.date = datetime.datetime.now()
                milestone.save()
            setattr(milestone, 'respSet', milestone.responsible.all())
            setattr(milestone, 'critically', random.randrange(1, 4))

        arProject.append(project)

    return {
        'title': u'Календарь ответственности',
        'projects': arProject,
        'arDays': arDays,
        'users': TaskWidgetManager.getUsersThatUserHaveAccess(request.user, headerValues['CURRENT_PROJECT'])
    }